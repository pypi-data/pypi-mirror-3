#
#    Copyright (C) 2002-2011  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# import stuff
import AccessControl, types, operator
from AccessControl.Permissions import view_management_screens, manage_properties,\
     access_contents_information
from StringIO import StringIO
from DateTime import DateTime
import Acquisition, string
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import REPLACEABLE
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.BastionBanking.ZCurrency import ZCurrency

from utils import _mime_str, assert_currency
from BLBase import *
from BLSubsidiaryLedger import BLSubsidiaryLedger
from BLTransactionTemplate import BLTransactionTemplate
from BLSubsidiaryAccount import BLSubsidiaryAccount
from BLAccount import BLAccount, addBLAccount
from BLProcess import BLProcess
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Exceptions import LedgerError, ProcessError
from Products.CMFCore import permissions
from interfaces.process import IProcess

from zope.interface import Interface, implements

class IShareholderLedger(Interface): pass

manage_addBLShareDefinitionForm = PageTemplateFile('zpt/add_sharedefinition', globals())
def manage_addBLShareDefinition(self, id, title='', face=None, allocated=0,
                                issue_date=None, voting_class='A', REQUEST=None):
    """
    """
    if not face:
        face = ZCurrency('%s 1.00' % self.defaultCurrency())
    elif not isinstance(face, ZCurrency):
        face = ZCurrency(face)
    self._setObject(id, BLShareDefinition(id, 
                                          title, 
                                          face,  
                                          allocated, 
                                          issue_date or DateTime(), 
                                          voting_class))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return id

class BLShareDefinition( PropertyManager, BSimpleItem ):
    """
    The definition of a company share
    """
    meta_type = portal_type = 'BLShareDefinition'
    _properties = ( 
        {'id':'id',             'type':'string',   'mode':'r'},
        {'id':'title',          'type':'string',   'mode':'w'},
        {'id':'face',           'type':'currency', 'mode':'r'},
        {'id':'allocated',      'type':'long',     'mode':'w'},
        {'id':'issue_date',     'type':'date',     'mode':'w'},
        {'id':'voting_class',   'type':'string',   'mode':'w'},
        )

    property_extensible_schema__ = 0
    __ac_permissions__ = (
        (view, ('allotted', 'shareholders')), #TODO - fix this (ie FSEntryTemplate permissions!!)
        (OperateBastionLedgers, ('manage_propertiesForm', 'manage_editProperties','editProperties')),
        )

    default_page = 'blshare_view'
    voting_class = ''

    manage_options = (
        { 'label':'Properties', 'action':'manage_propertiesForm',
          'help':('BastionLedger', 'share_defs.stx') },
        ) + BSimpleItem.manage_options

    def __init__(self, id, title, face, allocated, issue_date, voting_class):
        assert_currency(face)
        self.id = id
        self.title = title
        self.face = face
        self.allocated = allocated
        self.issue_date = issue_date
        self.voting_class = voting_class

    def Title(self):
        return self.title

    def shareholders(self,effective=None):
        """
        return a list of shareholders who have allotments of this share
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        return self.aq_parent.getShareholdersWithShare(self.getId(), effective or DateTime())
    
    def allotted(self, effective=None):
        """ go sum up quantities of stock in shareholder accounts allocations """
        result = 0
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        for shareholder in self.shareholders():
            result += shareholder.allocationQuantity(self.getId(), effective or DateTime())
        return result

    def editProperties(self, title, description, face, allocated, issue_date, voting_class):
        """
        Plone edit
        """
        self._updateProperty('title', title)
        self.description = description
        self._updateProperty('face', face)
        self._updateProperty('allocated', allocated)
        if not isinstance(issue_date,DateTime):
            issue_date = DateTime(issue_date)
        self._updateProperty('issue_date', issue_date)
        self._updateProperty('voting_class', voting_class)
        self.reindexObject()

    def getCalls(self):
        """ returns any call objects associated with this definition """
        if self.fullyPaid():
            return []
        if not getattr(aq_base(self), 'calls', None):
            self.calls = Folder('calls')
        return self.calls.objectValues('BLCall')

    def fullyPaid(self, effective=None):
        """
        return whether or not all allocations are fully paid
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        for allocation in self.allotments():
            if not allocation.fullyPaid():
                return False
        return True

    def paidUp(self, effective=None):
        """
        return the pro-rated paid-up number of shares
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        total = ZCurrency(self.face.currency(), 0)
        for allotment in self.allotments():
            total += allotment.paid()
        return total

    def outstanding(self, effective=None):
        """
        return total callable
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        total = ZCurrency(self.face.currency(), 0)
        for allotment in self.allotments():
            total += allotment.outstanding()
        return total


    def maxCallablePercentage(self, effective=None):
        """
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        result = 0

        for allotment in self.allotments():
            amax = allotment.maxCallablePercentage()
            if amax and amax > result:
                result = amax

        return result

    def allotments(self, effective=None):
        """
        return all the allotments for this definition
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        results = []
        for shareholder in self.shareholders(effective):
            results.extend(shareholder.allocationValues(self.getId(), effective))
        return results

    def __cmp__(self, other):
        if not isinstance(other, BLShareDefinition):
            return -1

        my_id = self.getId()
        other_id = other.getId()

        if my_id > other_id:
            return -1
        elif my_id < other_id:
            return 1
        return 0

AccessControl.class_init.InitializeClass( BLShareDefinition )


manage_addBLAllocationForm = PageTemplateFile('zpt/add_allocation', globals())
def manage_addBLAllocation(self, id, definition=None, quantity=0, issue_date=DateTime(),
                           percentage=100, REQUEST=None):
    """
    """
    realself = self.this()
    if definition is None:
        definition = realself.blLedger().shareDefinitionValues()[0].getId()
    self._setObject(id, BLAllocation(id, definition, quantity, issue_date, percentage))
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])
    return id


class BLAllocation( PropertyManager, BSimpleItem ):
    """
    """
    meta_type = portal_type = 'BLAllocation'

    _properties = ( 
        {'id':'id',                'type':'string',    'mode':'r'},
        {'id':'definition',        'type':'selection', 'mode':'w', 'select_variable':'definitions'},
        {'id':'quantity',          'type':'long',      'mode':'w'},
        {'id':'percentage_paid',   'type':'float',     'mode':'w'},
        {'id':'issue_date',        'type':'date',      'mode':'w'},
        )

    __ac_permissions = (
        (OperateBastionLedgers, ('manage_propertiesForm', 'manage_editProperties','editProperties')),
        ) + BSimpleItem.__ac_permissions__

    manage_options = PropertyManager.manage_options + BSimpleItem.manage_options

    default_page = 'blallocation_view'
    percentage_paid = 100.0

    def __init__(self, id, definition, qty, issue_date, percentage_paid):
        self.id = id
        self.definition = definition
        self.quantity = qty
        self.issue_date = issue_date
        self.percentage_paid = percentage_paid

    def Title(self):
        """
        if set up, return the issue dated definition title, otherwise just the issue date
        """
        try:
            return "%s - %s" % (self.toLocalizedTime(self.issue_date), self.getDefinition().Title())
        except:
            # hmmm - some old imports are failing ...
            try:
                return self.toLocalizedTime(self.issue_date)
            except:
                return ''

    def editProperties(self, quantity, definition, issue_date, percentage_paid):
        """
        update the quantity, definition
        """
        self._updateProperty('quantity', quantity)
        self._updateProperty('definition', definition)
        self._updateProperty('issue_date', issue_date)
        self._updateProperty('percentage_paid', percentage_paid)

    def getDefinition(self):
        """
        returns the share definition associated with this allocation
        """
        return self.aq_parent.aq_parent._getOb(self.definition)

    def definitions(self):
        return map(lambda x: x.getId(), self.shareDefinitionValues())

    def getCalls(self):
        """
        return a list of call metadata
        """
        return self.getDefinition().getCalls()

    def nominal(self):
        """
        return the nominal value of the allocation
        """
        # hmmm - force it not to do int (repeat) processing - strangely this appears
        # to be returning a sequence ....
        face = self.getDefinition().face
        assert_currency(face)
        return face * float(self.quantity)

    def outstanding(self):
        """
        return any outstanding amount on the allocation
        """
        return self.nominal() * (100.0 - self.percentage_paid) / 100.0

    def paid(self):
        """
        return the paid-up value of the parcel
        """
        return self.nominal() * self.percentage_paid / 100.0
        

    def fullyPaid(self):
        return self.percentage_paid >= 100

    def votingClass(self):
        """ return it's voting class - if blank, this is a non-voting share """
        return self.getDefinition().voting_class 

    def maxCallablePercentage(self):
        return 100.0 - self.percentage_paid

    def _repair(self):
        if not getattr(aq_base(self), 'issue_date', None):
            self.issue_date = self.CreationDate()
        if not getattr(aq_base(self), 'definition', None):
            self.definition = self.getId()

AccessControl.class_init.InitializeClass( BLAllocation )

def manage_addBLCall(self, allocation_id, percentage, call_date, required_date, REQUEST=None):
    """
    """
    self._setObject(id, BLCall(id, allocation_id, percentage, call_date, required_date))

    return id
                    

class BLCall(PropertyManager, BSimpleItem):
    """
    """
    meta_type = portal_type = 'BLCall'

    _properties = ( 
        {'id':'id',            'type':'string',    'mode':'r'},
        {'id':'allocation_id', 'type':'selection', 'mode':'w', 'select_variable':'allocation_ids'},
        {'id':'percentage',    'type':'float',     'mode':'w'},
        {'id':'call_date',     'type':'date',      'mode':'w'},
        {'id':'required_date', 'type':'date',      'mode':'w'},
        )

    def __init__(self, id, allocation_id, percentage, call_date, required_date):
        self.id = id
        self.allocation_id = allocation_id
        self.call_date = call_date
        self.required_date = required_date

    def manage_post(self, REQUEST=None):
        """
        post the call to affected shareholders
        """

    

AccessControl.class_init.InitializeClass(BLCall)


manage_addBLShareholderForm = PageTemplateFile('zpt/add_shareholder', globals())
def manage_addBLShareholder(self, id='', title='', description='', currency='', REQUEST=None):
    """
    """
    #assert accounts.meta_type == 'BLAccounts', 'Incorrect container: %s <> BLShareholderLedger' % self.meta_type
    if not currency:
        currency = self.defaultCurrency()
    if not id:
        id = self.nextAccountId()
    type = self.controlAccount().type
    self._setObject(id, BLShareholder(id, title, description, type, currency))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return id

def addBLShareholder(self, id, title=''):
    """ Plone ctor """
    id = manage_addBLShareholder(self, id=id, title=title)
    return id

class BLShareholder(BLSubsidiaryAccount):
    """ """
    meta_type = portal_type = 'BLShareholder'

    __ac_permissions = BLSubsidiaryAccount.__ac_permissions__ +(
        (access_contents_information, ('allocationValues', 'allocationQuantity', 'shareDefinitionValues')),
        (view_management_screens, ( 'manage_allocations', 'manage_notices') ),
        (OperateBastionLedgers, ('manage_details',)),
        )

    # we want to be able to shove allocations named as their share def
    __replaceable__ = REPLACEABLE
    
    _properties =  BLSubsidiaryAccount._properties + (
        {'id':'address',        'type':'text',      'mode': 'w'},
        {'id':'account_number', 'type':'string',    'mode': 'w'},
    )

    def manage_options(self):
        options = [ BLSubsidiaryAccount.manage_options(self)[0],
                    {'label':'Advices', 'action':'manage_notices'},
                    {'label':'Allocations', 'action':'manage_btree'}]
        options.extend(BLSubsidiaryAccount.manage_options(self)[1:])
        return options

    manage_notices = PageTemplateFile('zpt/shareholder_notices', globals())
    #index_html = PageTemplateFile('zpt/shareholderaccount_index', globals())

    def __init__(self, id, title, description, type, currency):
        BLSubsidiaryAccount.__init__(self, id, title, description, type, 'ShareHolder', currency, id)
        self.address=''
        self.email=''
        self.account_number=''

    def all_meta_types(self):
        return [ ProductsDictionary('BLAllocation') ]

    def allocationValues(self, definition='', effective=None):
        """
        returns a list of allocations of a share at given date, or all allocations
        for a given date
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        if definition:
            return filter(lambda x: x.issue_date <= effective and x.definition==definition,
                          self.objectValues('BLAllocation'))
        else:
            return filter(lambda x: x.issue_date <= effective, self.objectValues('BLAllocation'))

    def allocationQuantity(self, definition, effective=None):
        """
        returns physical quantity of a share held at given date
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        allocations = self.allocationValues(definition, effective)
        if allocations:
            return reduce(operator.add, map(lambda x: x.quantity, allocations))
        return 0

    def shareDefinitionValues(self, effective=None):
        """
        return a list of the stock types held by the shareholder at a given date
        """
        defs = []
        for allocation in self.allocationValues(effective=effective):
            defn = allocation.definition
            if defn not in defs:
                defs.append(defn)

        if defs:
            return filter(lambda x: x.getId() in defs, self.aq_parent.shareDefinitionValues())
        
        return []

    def manage_emailShareCertificate(self, email, share, message=None,effective=DateTime(), REQUEST=None):
        """
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise ValueError, 'no MailHost found'
        
        sender = self.aq_parent.email
        if not sender:
            if REQUEST:
                REQUEST.set('manage_tabs_message', """Ledger's Correpondence Email unset!""")
                return self.manage_main(self, REQUEST)
            raise LedgerError, """Ledger's Correspo/ndence Email unset!"""

        effective=effective or DateTime()

        # ensure 7-bit
        mail_text = str(self.blsharecert_template(self, REQUEST, 
                                                  sender=sender, 
                                                  share=self.aq_parent.shareDefinition(share),
                                                  quantity=self.allocationQuantity(share,effective),
                                                  email=email, 
                                                  effective=effective))

        mailhost._send(sender, email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Statement emailed to %s' % email)
            return self.manage_main(self, REQUEST)

    def _repair(self):
        """
        """
        if getattr(aq_base(self), 'Allocations', None):
            for allocation in self.Allocations.objectValues():
                if not getattr(aq_base(self), allocation.getId(), None):
                    self._setObject(allocation.getId(), allocation)
        BLSubsidiaryAccount._repair(self)
            
AccessControl.class_init.InitializeClass( BLShareholder )
    
manage_addBLShareholderLedgerForm = PageTemplateFile('zpt/add_shareholderledger', globals())
def manage_addBLShareholderLedger(self, id, controlAccount, title='', REQUEST=None):
    """ adds a user container """
    try:
        # do some checking ...
        control = self.Ledger._getOb(controlAccount)
        assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
        #assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."
        self._setObject(id, BLShareholderLedger(id, title, control))
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return id

def addBLShareholderLedger(self, id, title='', REQUEST=None):
    """
    Plone Add
    """
    control = addBLAccount(self.Ledger, id, title)
    manage_addBLShareholderLedger(self, id, control, title=title)
    return id



class BLShareholderLedger ( BLSubsidiaryLedger ):
    """ """
    meta_type = portal_type = 'BLShareholderLedger'

    account_types = ('BLShareholder',)
    __ac_permissions__ = BLSubsidiaryLedger.__ac_permissions__ + (
        (access_contents_information, ('shareDefinitionValues', 'shareDefinition')),
        (OperateBastionLedgers, ('getShareholdersWithShare',) ),
        )

    implements(IShareholderLedger)

    #manage_mail = PageTemplateFile('zpt/view_shareholdermail', globals())
    
    def all_meta_types(self):
        t = BLSubsidiaryLedger.all_meta_types(self)
        t.append(ProductsDictionary('BLShareDefinition'))
        return t
    
    def __init__(self, id, title, control, account_prefix='S', txn_prefix='S' ):
        assert isinstance(control, BLAccount), "Invalid control account type!"
        BLSubsidiaryLedger.__init__(self, id, title, control, [ control.base_currency ],
                                    1000000, account_prefix, 1, txn_prefix )

    def getShareholdersWithShare(self, share_type, effective=None):
        """
        helper to return a list of shareholders holding a certain stock type
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        shareholders = []
        for shareholder in self.accountValues():
            if shareholder.allocationValues(share_type, effective or DateTime()):
                shareholders.append(shareholder)
        return shareholders

    def shareDefinitionValues(self):
        """
        """
        return self.objectValues('BLShareDefinition')

    def shareDefinition(self, id):
        """
        return the BLShareDefinition specified
        """
        try:
            defn = self._getOb(id)
        except:
            raise KeyError, id
        if not isinstance(defn, BLShareDefinition):
            raise KeyError, id
        return defn

    def _repair(self):
        if getattr(aq_base(self), 'Shares', None):
            for defn in self.Shares.objectValues():
                if not getattr(aq_base(self), defn.getId(), None):
                    self._setObject(defn.getId(), defn)
            try:
                delattr(self, 'Shares')
            except:
                pass
        BLSubsidiaryLedger._repair(self)

    def votingClasses(self):
        """
        return a list of voting class names for the ledger
        """
        results = {}
        for k in filter(lambda x:x,
                        map(lambda x: x.voting_class, 
                            self.shareDefinitionValues())):
            results[k] = 1
        return results.keys()

    def voters(self, effective=None):
        """
        return a list of userids of shareholder's (and proxy's) for all accounts
        with allocations with voting rights
        """
        voters = {}
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        for shareholder in self.accountValues(status='open'):
            if filter(lambda x: x.votingClass(),
                      shareholder.allocationValues(effective=effective)):
                for k in shareholder.getMemberIds():
                    voters[k] = 1
        return voters.keys()

    def votesForVoter(self, voting_class, userid, effective=None):
        """
        return the number of shares this user is eligible to vote for
        """
        total = 0
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        if type(voting_class) == types.StringType:
            voting_class = [ voting_class ]
        share_defs = filter(lambda x: x.voting_class in voting_class, 
                            self.shareDefinitionValues())

        mt = getToolByName(self, 'portal_membership')

        for share in share_defs:
            for shareholder in self.getShareholdersWithShare(share.getId(), effective):
                owners = shareholder.getMemberIds(mt)
                if userid in owners:
                    total += shareholder.allocationQuantity(share.getId(), effective)

        return total

    def voterInfoFor(self, userid, effective=None):
        """
        return a list of tuples, class, number of votes, for the specified user
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        # TODO - optimise all this ...
        results = []
        for vclass in self.votingClasses():
            total = self.votesForVoter(vclass, userid, effective)
            if total:
                results.append({'class':vclass, 
                                'votes':total, 
                                'joint':self.isJointHolding(vclass, userid, effective)})
        return results

    def voterInfo(self, effective):
        """
        return a list of voter info dictionaries
        """
        if not isinstance(effective, DateTime):
            effective = DateTime(effective)
        results = []
        for userid in self.voters(effective):
            info = self.voterInfoFor(userid)
            if info['votes']:
                info['userid'] = userid
                results.append(info)
        return results

    def isJointHolding(self, voting_class, userid, effective=None):
        """
        returns whether or not the class is a joint holding for voting
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        mt = getToolByName(self, 'portal_membership')
        for shareholder in self.getShareholdersWithShare(voting_class, effective or DateTime()):
            owners = shareholder.getMemberIds(mt)
            if userid in owners and len(owners) > 1:
                return True
        return False

    def otherHolders(self, voting_class, userid, effective=None):
        """
        return a list of other members jointly holding shares - an empty list 
        signifies a severally held share
        """
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        results = []
        mt = getToolByName(self, 'portal_membership')
        for shareholder in self.getShareholdersWithShare(voting_class, effective or DateTime()):
            owners = shareholder.getMemberIds(mt)
            if userid in owners and len(owners) > 1:
                for owner in filter(lambda x: x != userid):
                    if owner not in results:
                        results.append(owner)
        return results

AccessControl.class_init.InitializeClass( BLShareholderLedger )
    


def manage_addBLDividendAdvice(self, id, title, qty, type, amt, effective, REQUEST=None):
    """
    """
    assert self.this().meta_type == 'BLShareholder', 'doh - not a shareholder!'
    self._setObject(id, BLDividendAdvice(id, title, qty, type, abs(amt), effective))

    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])


class BLDividendAdvice(BSimpleItem):
    """
    A shareholder's dividend advice
    """
    meta_type = portal_type = 'BLDividendAdvice'

    implements(IProcess)

    manage_options = (
        {'label':'Advice', 'action':'manage_main'},
        {'label':'View',   'action':''},
        {'label':'Properties', 'action':'manage_propertiesForm'},
        ) + BSimpleItem.manage_options

    __ac_permissions__ = BSimpleItem.__ac_permissions__ + (
        (view, ('manage_download',)),
        )

    _properties = BSimpleItem._properties + (
        {'id':'quantity',       'type':'int',      'mode':'w'},
        {'id':'share_type',     'type':'string',   'mode':'r'},
        {'id':'amount',         'type':'currency', 'mode':'w'},
        {'id':'effective_date', 'type':'date',     'mode':'w'},
        )
    
    manage_main = PageTemplateFile('zpt/dividend_advice', globals())
    download_image = PageTemplateFile('zpt/dividend_advice_index', globals())

    default_page = 'bldividend_advice_view'

    def __init__(self, id, title, qty, type, amt, effective_date):
        self.id = id
        self.title = title
        self.quantity = qty
        self.share_type = type
        self.amount = amt
        self.effective_date = effective_date


    def manage_download(self, REQUEST, RESPONSE):
        """
        download the advice to local machine
        """
        RESPONSE.setHeader('Content-Type', 'application/octet-stream')
        RESPONSE.setHeader('Content-Disposition', 'filename=%s.html' % self.id)
        RESPONSE.write(self.download_image(self, REQUEST))

    def __cmp__(self, other):
        """
        sort order based upon effective date
        """
        other_dt = getattr(other, 'effective_date', None)
        if not other_dt:
            return 1
        if callable(other_dt):
            other_dt = other_dt()

        self_dt = self.effective_date

        if self_dt > other_dt: return 1
        if self_dt < other_dt: return -1
        return 0
        
AccessControl.class_init.InitializeClass(BLDividendAdvice)


class BLDividendProcess(BLProcess):
    """
    Paying a dividend
    """
    meta_type = portal_type = 'BLDividendProcess'

    parameterMap = (
        {'id':'share_type',   'title':'Share Type',   'type':'string',   'description':''},
        {'id':'total_amount', 'title':'Total Amount', 'type':'currency', 'description':''},
        {'id':'effective',    'title':'Effective',    'type':'date',     'description':''},
        {'id':'do_payment',   'title':'Do Payment?',  'type':'boolean',  'description':''},
        )
    
    def manage_run(self, share_type, total_amount, effective=None, do_payment=False):
        """
        """
        ledger = self.aq_parent
        if effective and not isinstance(effective, DateTime):
            effective = DateTime(effective)
        effective = effective or DateTime()
        sharedefn = getattr(ledger, share_type, None)

        if not sharedefn:
            raise ProcessError, 'Share Defnintion not found: %s' % share_type

        accounts = ledger.getShareholdersWithShare(share_type, effective)

        if not isinstance(total_amount, ZCurrency):
            total_amount = ZCurrency(total_amount)

        if not isinstance(effective, DateTime):
	    effective = DateTime(effective)

        if accounts:

            if do_payment:
                div_acc = 'dividend'
            else:
                div_acc = 'dividend_payable'

            payable = ledger.blp_dividend_payable.generate(accounts,
                                                           effective=effective,
                                                           total_amount=total_amount,
                                                           share_type=share_type,
                                                           dividend_account=div_acc)

            for shareholder in accounts:
                manage_addBLDividendAdvice(shareholder,
                                           '%s-%s' % (share_type, effective.strftime('%Y%m%d')),
                                           '%s Dividend' % share_type,
                                           shareholder.allocationQuantity(share_type, effective),
                                           share_type,
                                           payable.entry(shareholder.getId()).amount,
                                           effective)

            if do_payment:
                payment = self.blp_dividend_payment.generate(accounts,
                                                             effective=effective,
                                                             total_amount=total_amount,
                                                             share_type=share_type)

    def processFor(self, ledger):
        """
        conditions for which this process is available
        """
        if ledger.meta_type == 'BLShareholderLedger' and \
               ledger.shareDefinitionValues():
            return True
        return False
    
AccessControl.class_init.InitializeClass(BLDividendProcess)

#
# these are to be removed once conversions completed ...
#
class BLShareDefinitions( BObjectManager): pass
class BLAllocations( BObjectManager): pass
