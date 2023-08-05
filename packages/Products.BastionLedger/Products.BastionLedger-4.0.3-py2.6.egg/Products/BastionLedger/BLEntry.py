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

import AccessControl, logging, types, sys, traceback, string, uuid
from Acquisition import aq_base
from DateTime import DateTime
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from utils import floor_date, assert_currency
from BLBase import BSimpleItem, UUID_ATTR
from BLTransaction import BLTransaction
from AccessControl.Permissions import view, view_management_screens, manage_properties, \
     access_contents_information
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Exceptions import PostingError, AlreadyPostedError

from zope.interface import Interface, implements

LOG = logging.getLogger('BLEntry')

def _addEntry(self, klass, account, amount, title='', id=None):
    """
    helper to add an entry - with lots of validation checking
    """
    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    realself = self.this()
    assert isinstance(realself, BLTransaction), \
           'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert realself.status() in ('', 'incomplete', 'complete'), \
           'Woa - invalid txn state (%s)' % (str(realself))

    if not title:
        title = realself.title

    try:
        assert_currency(amount)
    except:
        try:
            amount = ZCurrency(amount)
        except:
            raise ValueError, "Not a valid amount: %s" % amount

    if amount == 0:
        raise ValueError,"Please post an amount"

    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    if not id:
        id = realself.generateId()
        
    if type(account) == types.StringType:
        account = getattr(self.Ledger, account)

    entry = klass(id, title, account.getId(), amount)
    realself._setObject(id, entry)
    
    return id

manage_addBLEntryForm = PageTemplateFile('zpt/add_entry', globals()) 
def manage_addBLEntry(self, account, amount, title='', id=None, REQUEST=None):
    """
    Add an entry - to a transaction ...

    account is either a BLAccount or an account id
    """
    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    realself = self.this()
    assert isinstance(realself, BLTransaction), \
           'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert realself.status() in ('', 'incomplete', 'complete'), \
           'Woa - invalid txn state (%s)' % (str(realself))

    if not title:
        title = realself.title

    try:
        assert_currency(amount)
    except:
        try:
            amount = ZCurrency(amount)
        except:
            message = "Not a valid amount: %s" % amount
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return realself.manage_main(realself, REQUEST)
            raise ValueError, message

    if amount == 0:
        message = "Please post an amount"
        if REQUEST is not None:
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return realself.manage_main(realself, REQUEST)
        raise ValueError, message

    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    if not id:
        id = realself.generateId()
        
    if type(account) == types.StringType:
        account = getattr(self.Ledger, account)

    entry = BLEntry(id, title, account.getId(), amount)
    realself._setObject(id, entry)
    
    if REQUEST is not None:
       return self.manage_main(self, REQUEST)

    # return the entry in context
    return id
    #return realself._getOb(id)

class IEntry(Interface): pass


class BLEntry( PropertyManager, BSimpleItem ):
    """
    An account/transaction entry

    Once the transaction has been posted, the entry has a date attribute
    Also, if there was any fx required, it will have an fx_rate attribute - from which the
    original currency trade may be derived ??
    """
    meta_type = portal_type = 'BLEntry'

    implements(IEntry)

    #  SECURITY MACHINERY DOES NOT LIKE PropertyManager.__ac_permissions__ '' ENTRY !!!!!!!!
    __ac_permissions__ = (
        (manage_properties, ('manage_addProperty', 'manage_editProperties',
                             'manage_delProperties', 'manage_changeProperties',
                             'manage_propertiesForm', 'manage_propertyTypeForm',
                             'manage_changePropertyTypes', )),
        (access_contents_information, ('hasProperty', 'propertyIds', 'propertyValues',
				       'propertyItems', 'getProperty', 'getPropertyType',
				       'propertyMap','blAccount', 'blTransaction',
                                       'blLedger', 'accountId', ), ('Anonymous', 'Manager')),
        (view, ('amountStr', 'absAmount', 'absAmountStr', 'isDebit', 'isCredit', 'status',
                'effective',  'reference', 'isPosting', 'isControlEntry', 'asCSV')),
        (OperateBastionLedgers, ('edit', 'setReference',)),
        (ManageBastionLedgers, ('manage_edit', 'manage_removePosting')),
        ) + BSimpleItem.__ac_permissions__

    #
    # we have some f**ked up stuff because id's may be used further up the aquisition path ...
    #
    __replaceable__ = 1

    manage_options =  (
        {'label': 'Details',    'action' : 'manage_main'},
        {'label': 'View',       'action' : ''},
        {'label': 'Properties', 'action' : 'manage_propertiesForm'},
        ) + BSimpleItem.manage_options

    manage_main = PageTemplateFile('zpt/view_entry', globals())
    manage_propertiesForm = PageTemplateFile('zpt/edit_entry', globals())

    property_extensible_schema__ = 0
    _properties = (
        { 'id'   : 'title',    'type' : 'string',    'mode' : 'w' },
        { 'id'   : 'ref',      'type' : 'string',    'mode' : 'w' },  # this seems to screw up!
        { 'id'   : 'account',  'type' : 'string',    'mode' : 'w' },
        { 'id'   : 'amount',   'type' : 'currency',  'mode' : 'w' },
        )

    def __init__(self, id, title, account, amount, ref=''):
        assert type(account) == types.StringType, "Invalid Account: %s" % account
        assert_currency(amount)
        self.id = id
        self.title = title
        # account is actually the account path from the Ledger
        self.account = account
        self.amount = amount
        self.ref = ref
        self.ledger = '' # only set on posting so we can back-ref to txn

    def Title(self):
        """
        return the description of the entry, guaranteed non-null
        """
        return self.title or self.blAccount().Title()

    def amountStr(self): return self.amount.strfcur()

    def amountAs(self, currency=''):
        """
        each entry may support two currencies, it's face currency and the posting currency
        """
        if currency == '' or self.amount.currency() == currency:
            return self.amount
        
        amount = getattr(self, 'posted_amount', None)
        if not amount or amount.currency() != currency:
            raise UnsupportedCurrency, '%s - %s' % (currency, str(self))
        return amount

    def absAmount(self, currency=''):
        return abs(self.amountAs(currency))

    def absAmountStr(self): return self.absAmount().strfcur()
    def isDebit(self): return self.amount > 0
    def isCredit(self): return not self.isDebit()

    def isPosting(self):
        """
        returns whether or not the entry is the 'posted' side - in an account
        """
        try:
            return not isinstance(self.aq_parent, BLTransaction)
        except AttributeError:
            # if we don't have an acquisition context ...
            return False

    def effective(self):
        """
        return the effective date of the entry - usually deferring to the effective
        date of the underlying transaction the entry relates to

        a None value represents a control entry
        """
        dt = getattr(aq_base(self), '_effective_date', None)
        if dt:
            return dt.toZone(context.timezone)
        try:
            txn = self.blTransaction()
            if txn:
                return txn.effective()
        except:
            # hmmm - don't want to crash spectacularly ...
            return None
        return None

    # stop shite getting into the catalog ...
    def _noindex(self): pass
    tags = type = subtype = accno = _noindex

    def blLedger(self):
        """
        return the ledger which I relate to (or None if I'm not yet posted)
        """
        return self.bastionLedger().Ledger

    def accountId(self):
        """
        returns the id of the account which the entry is posted/postable to
        """
        if self.account.find('/') != -1:
            return self.account.split('/')[1]
        return self.account

    def blAccount(self):
        """
        return the underlying account to which this affects
        """
        try:
            return self.blLedger()._getOb(self.accountId())
        except:
            pass
        return None

    def blTransaction(self):
        """
        A context independent way of retrieving the txn.  If it's posted then there
        are issues with the object id not being identical in container and object ...

        """
        parent = self.aq_parent
        if isinstance(parent, BLTransaction):
            return parent

        # I'm posted ...
        if self.ledger:
            ledger = parent.bastionLedger()._getOb(self.ledger)
        else:
            ledger = self.blLedger()

        # I must be in an account, acquire my Ledger's Transactions ...
        try:
            return ledger._getOb(self.getId())
        except (KeyError,AttributeError):
            if self.isControlEntry():
                return None
            
        raise AttributeError, '%s - %s' % (ledger, self)

    def _setEffectiveDate(self, dt):
        """
        some entry's don't belong to transaction's specifically, but we still want to give them a date
        """
        self._effective_date = floor_date(dt)
        self.unindexObject()
        self.indexObject()

    def edit(self, title, amount, posted_amount=None):
        """
        Plone edit
        """
        self._updateProperty('title', title)
        try:
            status = self.status()
            if not status in ('posted', 'reversed', 'cancelled', 'postedreversal'):
                self._updateProperty('amount', amount)
            # hmmm - allow posted-amount tweaks ...
            if posted_amount and getattr(aq_base(self), 'posted_amount', None):
                assert_currency(posted_amount)
                self.posted_amount = posted_amount
        except:
            pass
        
    def manage_edit(self, amount, title='', ref='', fx_rate='', posted_amount=None, REQUEST=None):
        """
        priviledged edit mode for experts only ...
        """
        self.manage_changeProperties(amount=amount,
                                     title=title,
                                     ref=ref)
        if type(fx_rate) == types.FloatType and isinstance(self.aq_parent, BLTransaction):
            self.fx_rate = fx_rate

        if posted_amount:
            self.posted_amount = ZCurrency(posted_amount)
            
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def isControlEntry(self):
        """
        returns if this is an entry for a control account
        """
        return False
    
    def __str__(self):
        """
        Debug representation
        """
        try:
            acct_str = self.blAccount().title
        except:
            acct_str = ''
            
        return "<%s instance - %s, %s, %s/%s %s (%s) at %s>" % (self.meta_type,
                                                                self.id,
                                                                self.effective(),
                                                                self.amount,
                                                                getattr(aq_base(self), 'posted_amount', '???'),
                                                                self.account,
                                                                acct_str,
                                                                self.absolute_url())

    __repr__ = __str__

    def indexObject(self):
        """ Handle indexing """
        cat = self.aq_parent.catalog()   # either BLTransactions or BLAccounts ..
        if cat.meta_type == 'BLAccounts':
            try:
                url = '/'.join(self.getPhysicalPath())
                cat.catalog_object(self, url)
            except:
                pass
        
    def unindexObject(self):
        """ Handle unindexing """
        cat = self.aq_parent.catalog() # either BLTransactions or BLAccounts ...
        try:
             url = '/'.join(self.getPhysicalPath())
             cat.uncatalog_object(url)
        except:
            pass

    def manage_removePosting(self, REQUEST=None):
        """
        delete a posting amount, use with care ...
        """
        if getattr(aq_base(self), 'posted_amount', None):
            delattr(self, 'posted_amount')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _setPostingAmount(self, force=False):
        """
        """
        if not force and getattr(aq_base(self), 'posted_amount', None):
            return

        target = self.aq_parent.defaultCurrency()
        base = self.amount.currency()

        if target == base:
            return

        if force or not getattr(aq_base(self), 'fx_rate', None):
            self.fx_rate = rate = getToolByName(self, 'portal_bastionledger').crossMidRate(base, 
                                                                                           target,
                                                                                           self.effective())
        else:
            rate = self.fx_rate

        self.posted_amount = ZCurrency(target, self.amount.amount() * rate)


    def _post(self, force=False):
        """
        write a copy of yourself to the account - changing id to txn id

        force causes any fx rate to be recalculated
        """
        txn = self.blTransaction()
        account = self.blAccount()
        id = txn.getId()
        # copy itself into the account using the parent txn id as the id
        entry = self._getCopy(self)

        entry.id = id
        entry.ledger = txn.blLedger().getId()

        # we need to make sure the entry has a different UUID ...
        if getattr(aq_base(self), UUID_ATTR, None):
            # this is plone.uuid.generator.UUID1Generator ...
            # something's also removing separators ...
            setattr(entry, UUID_ATTR, str(uuid.uuid4()).replace('-',''))

        # do any FX conversion ...
        base = txn.defaultCurrency()
        target = self.amount.currency()
        if target != base:
            self._setPostingAmount(force)

            # this posted amount *must* be the currency for the underlying ledger so any balance()
            # call will not have to risk doing an FX conversion ...
            entry.posted_amount = self.posted_amount

        # post it ...
        try:
            account._setObject(id, entry)
        except KeyError:
            if force:
                account._delObject(id, force=True)
                account._setObject(id, entry)
            else:
                raise AlreadyPostedError, (str(entry), str(account),list(account.objectItems()), str(txn))
        
        # return the posted entry
        return entry

    def setReference(self, value):
        self._updateProperty('ref', value)
        
    def reference(self):
        # return a string, or the underlying object if available ...
        if self.ref:
            try:
                return self.unrestrictedTraverse(self.ref)
            except:
                return self.ref
        return ''

    def status(self):
	"""
	my status is the status of my transaction ...
	"""
        try:
            txn = self.blTransaction()
            if txn:
                # hmmm - this is old cruft and only here to support really old imports ...
                if not callable(txn.status):
                    return txn.status
                return txn.status()
        except:
            pass
        # OK - must be a special entry ...
        return 'posted'

    def _repair(self):
        #
        # date is irrelevant on the entry - it's an attribute of the txn ...
        #
        if getattr(aq_base(self), 'date', None):
            delattr(self, 'date')

    def _updateProperty(self, name, value):
        """
        do a status check on the transaction after updating amount
        """
        # we don't update any entries except those in Transactions - ie not posted ...
        #if not isinstance(self.aq_parent, BLTransaction) and name not in ('ref', 'title', 'ledger'):
        #    return
        
        PropertyManager._updateProperty(self, name, value)
        if name == 'amount' and isinstance(self.aq_parent, BLTransaction):
            self.aq_parent.setStatus()

    def __add__(self, other):
	"""
	do any necessary currency conversion ...
	"""
        if not isinstance(other, BLEntry):
	    raise TypeError, other

	if not other.account == self.account:
	    raise ArithmeticError, other

        other_currency = other.amount.currency()
        self_currency = self.amount.currency()
        if other_currency != self_currency:
            rate = self.portal_bastionledger.crossMidRate(self_currency, other_currency, self.effective())
	    entry = BLEntry(self.getId(), 
			    self.title,
                            self.account, 
                            ZCurrency(self_currency, (other.amount.amount() * rate + self.amount.amount())), 
                            self.ref)
	    entry.fx_rate = rate
	    return entry
	else:
	    return BLEntry(self.getId(), 
                           self.title, 
                           self.account, 
                           other.amount + self.amount,
                           self.ref)

    def asCSV(self, datefmt='%Y/%m/%d'):
        """
        """
        txn = self.blTransaction()
        account = self.blAccount()
        amount = self.amount
        return ','.join((self.getId(),
                         self.ledger or txn and txn.aq_parent.getId() or '',
                         txn and txn.getId() or '',
                         '"%s"' % self.Title(),
                         txn and '"%s"' % txn.effective_date.toZone(self.timezone).strftime(datefmt) or '',
                         amount.currency(),
                         str(amount.amount()),
                         account.accno or '',
                         account.Title() or '',
                         self.status()))

    def __cmp__(self, other):
        """
        sort entries on effective date
        """
        other_dt = getattr(other, 'effective', None)
        if not other_dt:
            return 1
        if callable(other_dt):
            other_dt = other_dt()

        self_dt = self.effective()

        if self_dt < other_dt: return 1
        if self_dt > other_dt: return -1
        return 0

    def postingEntry(self):
        """
        the entry in the transaction from which the posted entry was/will be generated
        """
        if self.isPosting():
            return self
        return self.blTransaction().entry(self.accountId())

    def postedEntry(self):
        """
        if the transaction is posted, then the corresponding entry in the affected account,
        otherwise None
        """
        if not self.isPosting():
            return self

        acc = self.blAccount()
        tid = self.aq_parent.getId()
        try:
            return acc._getOb(tid)
        except (KeyError, AttributeError):
            pass

        return None

AccessControl.class_init.InitializeClass(BLEntry)

