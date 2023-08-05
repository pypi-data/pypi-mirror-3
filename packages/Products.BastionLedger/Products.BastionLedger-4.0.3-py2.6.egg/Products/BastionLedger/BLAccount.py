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

import AccessControl, logging, string, operator, transaction, types
from AccessControl.Permissions import view, view_management_screens,\
     manage_properties, access_contents_information
from Acquisition import aq_base
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog

from utils import floor_date, ceiling_date, assert_currency, isDerived
from BLBase import ProductsDictionary, BSimpleItem, BObjectManager, BObjectManagerTree
from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from BLEntry import manage_addBLEntry, BLEntry
from BLTransaction import manage_addBLTransaction
from BLGlobals import EPOCH, MAXDT
from BLAttachmentSupport import BLAttachmentSupport
from BLTaxCodeSupport import BLTaxCodeSupport
from Exceptions import PostingError, OrphanEntryError, IncorrectAmountError, LedgerError

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

from Products.CMFCore.utils import getToolByName

from zope.interface import Interface,implements

class IAccount(Interface): pass

LOG = logging.getLogger('BLAccount')
#
# temporary hack to map new subtype field (works for UK_General/Australia...)
#
SUBTYPES = { 1000 : 'Current Assets',
             1500 : 'Inventory Assets',
             1800 : 'Capital Assets',
             2000 : 'Current Liabilities',
             2200 : 'Current Liabilities',
             2600 : 'Long Term Liabilities',
             3300 : 'Share Capital',
             3500 : 'Retained Earnings',
             4000 : 'Sales Revenue',
             4300 : 'Consulting Revenue',
             4400 : 'Other Revenue',
             5000 : 'Cost of Goods Sold',
             5400 : 'Payroll Expenses',
             5500 : 'Taxation Expenses',
             5600 : 'General and Administrative Expenses' }

manage_addBLAccountForm = PageTemplateFile('zpt/add_account', globals()) 
def manage_addBLAccount(self, title,  currency, type, subtype='', accno='', tags=[], id='', description='',REQUEST=None):
    """ an account """

    self = self.this()

    # hmmm - factory construction kills this ...
    #if accno in self.Accounts.uniqueValuesFor('accno'):
    #    raise LedgerError, 'Duplicate accno: %s' % accno

    if not id:
        id = self.nextAccountId()

    assert currency in CURRENCIES, 'Unknown currency type: %s' % currency
    try:
        self._setObject(id, BLAccount(id, title, description, type, subtype, currency, accno or id, tags))
    except:
        # TODO: a messagedialogue ...
        raise
    
    acct = self._getOb(id)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % acct.absolute_url())
        
    return acct

def addBLAccount(self, id='', title='', type='Asset', subtype='Current Asset', accno='', REQUEST=None):
    """
    Plone constructor
    """
    # hmmm - this becomes a TempFolder when plugged into portal_factories ...
    #assert self.meta_type=='BLLedger', 'wrong container type: %s != BLLedger' % self.meta_type

    account = manage_addBLAccount(self,
                                  id = id,
                                  title=title,
                                  type=type,
                                  subtype=subtype,
                                  accno=accno or id,
                                  currency=self.defaultCurrency())
    return account.getId()

class BLAccount(BObjectManagerTree, BLAttachmentSupport, BLTaxCodeSupport):
    """
    """
    meta_type = portal_type = 'BLAccount'

    implements(IAccount)
    
    __ac_permissions__ =  (
        (access_contents_information, ('zeroAmount', 'Currencies', 'hasTag', 'allTags')),
        (view_management_screens, ('manage_statement', 'manage_btree', 'manage_verify', 'manage_mergeForm')),
        (ManageBastionLedgers, ('manage_details', 'manage_acl', 'manage_edit',
                                'manage_setDescriptionFromEntryAccount',
                                'manage_addTaxGroup', 'manage_delTaxGroups',
                                'manage_editTaxCodes', 'manage_addTaxCodes', 'manage_merge')),
	(OperateBastionLedgers, ('createTransaction', 'createEntry', 'manage_statusModify',
				 'updateProperty', 'updateTags')),
        (view, ('blLedger', 'balance', 'total', 'debitTotal', 'creditTotal', 'manage_emailStatement',
	        'prettyTitle', 'entries', 'entryValues', 'entryItems', 'subtypes', 'modificationTime',
                'openingBalance', 'openingDate', 'balances', 'historicalDates',
                'getBastionMerchantService', 'isFCA')),
        ) + BObjectManagerTree.__ac_permissions__ + BLAttachmentSupport.__ac_permissions__

    _properties = BObjectManagerTree._properties + (
        {'id':'base_currency', 'type':'selection', 'mode':'w', 'select_variable':'Currencies'},
        {'id':'type',          'type':'selection', 'mode':'w', 'select_variable':'Types'},
        {'id':'subtype',       'type':'string',    'mode':'w', },
        {'id':'accno',         'type':'string',    'mode':'w', },
        {'id':'tags',          'type':'lines',     'mode':'w', },
    )

    #default_page = 'blaccount_view'

    # Plone requirement - not used
    description = ''

    # just for emergencies ....
    manage_btree = BObjectManagerTree.manage_main

    def manage_options(self):
        options = [ {'label': 'Statement', 'action': 'manage_statement',
                     'help':('BastionLedger', 'statement.stx') },
                    {'label':'View', 'action':'',},
                    {'label': 'Details', 'action': 'manage_details',
                     'help':('BastionLedger', 'account_props.stx') },
                    {'label':'Verify', 'action':'manage_verify',},
                    {'label':'Tax Groups', 'action':'manage_taxcodes'},
                    {'label':'Merge', 'action':'manage_mergeForm' },
                    BLAttachmentSupport.manage_options[0],]
        if getattr(aq_base(self), 'acl_users', None):
            options.append( {'label': 'Users', 'action':'manage_acl'} )
        options.extend(BObjectManagerTree.manage_options[2:])
        return options

    Types = ('Asset', 'Liability', 'Proprietorship', 'Income', 'Expense')

    manage_statement = manage_main = PageTemplateFile('zpt/view_account', globals())
    manage_details   = PageTemplateFile('zpt/edit_account', globals())
    manage_acl       = PageTemplateFile('zpt/view_acl', globals())
    manage_mergeForm = PageTemplateFile('zpt/merge_accounts', globals())


    def action_buttons(self):
        """
        some html defining some action(s) on the account
        """
        return ""

    def catalog(self):
        return self.aq_parent.Accounts

    def Currencies(self):
        """
        A list of approved currencies which this account may be based
        """
        return self.aq_parent.currencies

    def isFCA(self):
        """
        return whether or not this is a foreign currency account - not of the same
        currency as the ledger
        """
        return self.base_currency != self.aq_parent.defaultCurrency()

    def optional_objects(self):
        objs = []
        if getattr(aq_base(self), 'acl_users', None):
            objs.append({'id':'acl_users', 'name': self.acl_users.meta_type})
        return objs

    def __init__(self, id, title, description, type, subtype, currency, accno,
                 tags=[], opened=DateTime()):
        BObjectManagerTree.__init__(self, id)
        self.opened = floor_date(opened)
        self._updateProperty('base_currency', currency)
        self._updateProperty('title', title)
        self.description = description
        self._updateProperty('type', type)
        self._updateProperty('subtype', subtype)
        self._updateProperty('accno', accno)
        self._updateProperty('tags', tags)

    def updateTags(self, tags):
        """
        """
        if type(tags) == types.StringType:
            tags = (tags,)
        self._updateProperty('tags', tags)
        self.reindexObject(idxs=['tags'])

    def manage_edit(self, title, description, type, subtype, accno, tags, base_currency='', REQUEST=None):
        """ """
        # only change currency if there are no entries ...
        #if base_currency and base_currency != self.base_currency and not len(self):
        if base_currency and base_currency != self.base_currency:
            self._updateProperty('base_currency', base_currency)

        self.manage_changeProperties(title=title, 
                                     description=description, 
                                     type=type,
                                     subtype=subtype,
                                     accno=accno,
                                     tags=tags)
        self.reindexObject()
        if REQUEST is not None:
            REQUEST.set('management_view', 'Details')
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_details(self, REQUEST)

    def manage_merge(self, ids=[], delete=True, REQUEST=None):
        """
        move entries from nominated account(s) into this one, adjusting their postings
        and removing those account(s) from the ledger if delete
        """
        merged = 0
        ledger = self.aq_parent

        for id in ids:
            try:
                account = ledger._getOb(id)
            except:
                continue

            # we need to take a copy because otherwise we're unindexing stuff we previously
            # had just indexed with the account number changes/substitutions ...
            for v in list(account.objectValues()):
                k = v.getId()
                account._delObject(k)
                if isinstance(v, BLEntry):
                    # adjust the posted entry
                    v.account = '%s' % self.getId()
                    # adjust the original pre-posting in the transaction
                    txn = v.blTransaction()
                    txn.entry(account.getId()).account = '%s' % self.getId()
                self._setObject(k, v)

            # remove the old account
            if delete:
                ledger._delObject(id)
            merged += 1
            
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'merged %i accounts' % merged)
            return self.manage_main(self, REQUEST)


    def manage_verify(self, REQUEST=None):
        """
        verify the account entries have been applied correctly and are still valid

        this function deliberately *does not* use the underlying object's methods
        to check this - it's supposed to independently check the underlying
        library - or consequent tamperings via the ZMI
        """
        bad_entries = []
        ledger_id = self.aq_parent.getId()
        for posted in self.entryValues():
            try:
                txn = posted.blTransaction()
            except:
                bad_entries.append((OrphanEntryError(posted), ''))
                continue
            if txn is None:
                if posted.isControlEntry():
                    continue

                bad_entries.append((OrphanEntryError(posted), ''))
                continue
            
            if txn.status() not in ('posted', 'reversed', 'postedreversal'):
                bad_entries.append((PostingError(posted), ''))
                continue
                
            try:
                unposted = txn.entry(self.getId(), ledger_id)
            except KeyError:
                #raise KeyError, (str(txn), self.getId(), ledger_id)
                bad_entries.append((OrphanEntryError(posted), ''))
                continue

            # find/use common currency base
            base_currency = self.base_currency

            unposted_amt = unposted.amount
            posted_amt = posted.amount

            if unposted_amt.currency() != base_currency:
                unposted_amt = unposted.amountAs(base_currency)

            if posted_amt.currency() != base_currency:
                posted_amt = posted.amountAs(base_currency)

            # 5 cent accuracy ...
            if abs(unposted_amt - posted_amt) > 0.05:
                bad_entries.append((IncorrectAmountError(posted), 
                                    '%s - %s' % (unposted_amt, unposted_amt - posted_amt)))

        if REQUEST:
            if bad_entries:
                REQUEST.set('manage_tabs_message',
                            '<br>'.join(map(lambda x: "%s: %s %s" % (x[0].__class__.__name__,
                                                                     html_quote(str(x[0].args[0])),
                                                                     x[1]), bad_entries)))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)
        
        return bad_entries

    def manage_emailStatement(self, email, message='', effective=None, REQUEST=None):
        """
        email invoice to recipient ...
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
                
        # ensure 7-bit
        mail_text = str(self.blaccount_template(self, self.REQUEST, sender=sender, 
                                                email=email, effective=effective or DateTime()))

        mailhost._send(sender, email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Statement emailed to %s' % email)
            return self.manage_main(self, REQUEST)

    def manage_setDescriptionFromEntryAccount(self, REQUEST=None):
        """
        sometimes people stick naf transaction descriptions and this goes and applies
        underlying account title to the description - this is only used against Subsidiary Ledger postings
        """
        for entry in map(lambda x: x[1], self.entries()):
            try:
                # alright - there is most likely only one subsidiary entry in a subsidiary transaction ...
                entry.title = entry.blTransaction().objectValues('BLSubsidiaryEntry')[0].Account().prettyTitle()
            except:
                pass
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _updateProperty(self, name, value):
        if name == 'base_currency':
            if not value in CURRENCIES:
                raise UnsupportedCurrency, value
        if name == 'accno':
            # go change it in periods (if we've got context - ie - not a ctor call)
            periods = getattr(self, 'periods', None)
            if periods:
                for period in periods.periodsForLedger(self.getId()):
                    try:
                        period._getOb(self.getId()).accno = value
                    except KeyError:
                        pass
        BObjectManagerTree._updateProperty(self, name, value)


    def blLedger(self):
        """
        find the BLLedger (derivative) of this account - in any circumstance
        """
        parent = self.aq_parent

        if not isDerived(parent.__class__, 'LedgerBase'):
            parent = parent.aq_parent

        return parent


    def balance(self, currency=None, effective=None, *args, **kw):
        """
        return the account balance in specified currency, as of date (defaults to all)
        """
        currency = currency or self.base_currency

        # figure out if we can use a cached beginning value
        # TODO - we could incorporate period info sums into this as well
        opening_dt = self.openingDate(effective)
        opening_amt = self.openingBalance(opening_dt)
        
        if not effective:
            dtrange = (opening_dt, DateTime())
        elif isinstance(effective, DateTime):
            if effective >= opening_dt:
                dtrange = (opening_dt, ceiling_date(effective))
            else:
                # hmmm - this shouldn't happen ...
                dtrange = (opening_dt, effective)
        elif type(effective) in (types.ListType,types.TupleType):
            dtrange = effective
        else:
            raise AttributeError, dtrange

        if opening_amt.currency() != currency:
            pt = getToolByName(self, 'portal_bastionledger')
            total = pt.convertCurrency(opening_amt, opening_dt, currency)
        else:
            total = opening_amt

        # decide if opening amount is sufficient for the query ...
        if opening_dt >= max(dtrange):
            return total

        #raise AssertionError,(opening_dt, dtrange, total)
        return total + self.total(currency=currency, effective=dtrange)
                                       
    def total(self, effective=None, currency=None):
        """
        summates entries over range
        """
        amts = []
        currency = currency or self.base_currency

        # summate the entries ...
        for entry in self.entryValues(effective, status=('posted')):
            if entry.isControlEntry():
                # only do control entry query if it's value isn't already incorporated in opening balance
                opening_dt = entry.lastTransactionDate()
                if opening_dt < min(effective):
                    continue
                amts.append(entry.total(effective=effective, currency=currency))
            else:
                amts.append(entry.amountAs(currency))

        return self._total(amts, effective, currency)
        

    def debitTotal(self, effective=None, currency=None):
        """
        sum up the debits
        effective_date can be a single value or a list with a single element, in which case, we return
        all debits until that date.  If effective_date is a multi-element list, then we sum the entries
        within that range
        """
        currency = currency or self.base_currency
        return self._total(map(lambda x: x.amountAs(currency),
                               filter(lambda x: x.amount > 0, self.entryValues(effective,status=('posted',)))),
                           effective, currency)

    def creditTotal(self, effective=None, currency=None):
        """
        sum up the credits (filtering out any reversals)
        effective_date can be a single value or a list with a single element, in which case, we return
        all credits until that date.  If effective_date is a multi-element list, then we sum the entries
        within that range
        """
        currency = currency or self.base_currency
        return self._total(map(lambda x: x.amountAs(currency),
                               filter(lambda x: x.amount < 0, self.entryValues(effective,status=('posted',)))),
                           effective, currency)

    def _total(self, amounts, effective=None, currency=None):
        # can't reduce an empty lost ...
        if amounts:
            total = reduce(operator.add, amounts)
        else:
            total = ZCurrency(currency or self.base_currency, 0.0)

        if currency and total.currency() != currency:
            if effective:
                if type(effective) in (types.ListType, types.TupleType):
                    eff = max(effective)
                else:
                    if not isinstance(effective, DateTime):
                        raise ValueError, effective
                    eff = effective
            else:
                eff = DateTime()

            pt = getToolByName(self, 'portal_bastionledger')
            return pt.convertCurrency(total, eff, currency)

        return total
        
    def hasForwards(self, dt=None):
        """
        returns whether or not there are forward-dated transactions
        """
        dt = dt or DateTime()
        return len(self.entryItems(effective=(dt,MAXDT))) != 0
        
    def historicalDates(self):
        """
        returns a list of (cached) end dates from which to offer 'nice' summary
        calculation ranges
        """
        dates = map(lambda x: x.period_ended,
                    self.periods.periodsForLedger(self.aq_parent.getId()))
        dates.reverse()
        return dates

    def openingBalance(self, effective=None, currency=''):
        """
        return the amount as per the effective date (as summed past the last period end)
        """
        effective = effective or DateTime()
        currency = currency or self.base_currency

        # income and expense accounts are always closed out at period-end - unfortunately except
        # the post/correction entries ...
        #if self.type in ('Expense', 'Income'): 
        if self.type in (): 
            balance = self.zeroAmount()
        else:
            try:
                balance = self.periods._balanceForAccount(effective, self.aq_parent.getId(), self.getId())
            except:
                balance = self.total(currency=currency, effective=(EPOCH,effective))

        return balance


    def openingDate(self, effective=DateTime()):
        """
        return the date for which the opening balance applies
        """
        last_closing = self.periods.lastClosingForLedger(self.aq_parent.getId(), effective)
        if last_closing != EPOCH:
            return floor_date(last_closing + 1)
        return floor_date(last_closing)
    
    def prettyTitle(self):
        """
        seemly title - even in face of portal_factory creation ...
        """
        return "%s - %s" % (self.accno or self.getId(), self.title or self.getId())
        
    def entryItems(self, effective=[], status=('posted',), query={}, REQUEST=None):
        """
        returns all entries in given status's - defaulted to filter cancelled status

        query is a hash, keyed on 'accno' which is the account id, 'debit', and 'credit', 'desc', 'case_sensitive'
        """
        # add control entries to top of list - regardless of balance for the date range!!
        entries = map(lambda x: (x.getId(), x),
                      map(lambda x: x.blEntry(effective=effective), 
                          self.objectValues('BLControlEntry')))

        if effective:
            entries.extend(self.objectItemsByDate('BLEntry', effective))
        else:
            entries.extend(list(self.objectItems('BLEntry')))

        if query:
            results = []
            # accnos are actually account ids!!
            accnos = query.get('accno', [])
            debit = query.has_key('debit')
            credit = query.has_key('credit')
            desc = query.get('desc','')
            case_sensitive = query.has_key('case_sensitive')
            
            if not case_sensitive:
                desc = desc.lower()

            else:
                results = list(entries)

            if accnos:
                for entry in entries:
                    e = entry[1]
                    # go check the other legs of the transaction to see if they match
                    txn = e.blTransaction()

                    for accno in accnos:
                        other = txn.entry(accno)
                        if other:
                            results.append(entry)
                            break
            else:
                results = list(entries)

            # next filter on descriptions
            if desc:
                results = filter(lambda x:
                                     not case_sensitive and x[1].title.lower().find(desc) != -1 or x[1].title.find(desc) != -1, entries)

            # lastly, blast out any of the wrong type
            if debit or credit:
                results = filter(lambda x: x[1].amount > 0 and debit or credit, results)

            entries = results

        return filter(lambda x, status=status: x[1].status() in status, entries)

    entries = entryItems

    def entryValues(self, effective=[], status=('posted','reversed','postedreversal'), query={}, REQUEST=None):
        """
        returns all entries in given status's - defaulted to filter cancelled
        """
        return map(lambda x: x[1], self.entryItems(effective, status, query))

    def entryIds(self, effective=[], status=('posted','reversed','postedreversal'), query={}, REQUEST=None):
        """
        returns all entries in given status's - defaulted to filter cancelled
        """
        return map(lambda x: x[0], self.entryItems(effective, status, query))

    def subtypes(self, type=''):
        if type:
            stypes = map( lambda x: x.subtype, self.Accounts(type=type) )
            ret = []
            for stype in stypes:
                if stype == '' or stype in ret:
                    continue
                ret.append(stype)
            return ret
        else:
            return self.aq_parent.uniqueValuesFor('subtype')
    
    def _delObject(self, id, tp=1, suppress_events=False, force=True):
        #
        # we are only going to delete subsidiary ledger control entries ...
        #  (these are identified as those without a transaction...)
        # or stuff associated with f**ked transactions ...
        #
        if force or self.expertMode():
            BObjectManagerTree._delObject(self, id, tp, suppress_events=suppress_events)
            return
        
        if id in ['acl_users',]:
            BObjectManagerTree._delObject(self, id, tp)
        else:
            ob = self._getOb(id)
            txn = getattr(aq_base(ob), id, None)
            if txn == None or txn.status() not in  ('posted', 'reversed', 'cancelled',
                                                    'postedreversal'):
                BObjectManagerTree._delObject(self, id, tp)
            else:
                LOG.debug( "BLAccount::_delObject(%s) doing nothing!!" % id)

    def modificationTime(self):
        """ """
        return self.bobobase_modification_time().strftime('%Y-%m-%d %H:%M')
            
    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name=prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value=REQUEST.get(name, '')
                self._updateProperty(name, value)

        self.reindexObject()


    def manage_delProperties(self, ids=[], REQUEST=None):
        """ only delete props NOT in extensions ..."""
        if REQUEST:
            # Bugfix for property named "ids" (Casey)
            if ids == self.getProperty('ids', None): ids = []
            ids = REQUEST.get('_ids', ids)
        extensions = self.aq_parent.aq_parent.propertyIds()
        ids = filter( lambda x,y=extensions: x not in y, ids )
        BObjectManagerTree.manage_delProperties(self, ids)
        if REQUEST:
            return self.manage_propertiesForm(self, REQUEST)
            
    
    def indexObject(self, idxs=[]):
        """ Handle indexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            url = '/'.join(self.getPhysicalPath())
            self.catalog().catalog_object(self, url, idxs)
        except:
            pass
        
    def unindexObject(self):
        """ Handle unindexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            url = '/'.join(self.getPhysicalPath())
            self.catalog().uncatalog_object(url)
        except:
            pass

    def reindexObject(self, idxs=[], REQUEST=None):
        """
        reappy the account to the catalog
        """
        if not idxs:
            self.unindexObject()
        self.indexObject(idxs=idxs)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'recataloged account')
            return self.manage_main(self, REQUEST)

    def createTransaction(self, title='', reference=None, effective=None):
        """
        polymorphically create correct transaction for ledger, returning this transaction
        """
        ledger = self.blLedger()
        tid = manage_addBLTransaction(ledger, '',
                                      title or self.getId(), 
                                      effective or DateTime(),
                                      reference)
        return ledger._getOb(tid)

    def createEntry(self, txn, amount, title=''):
        """ transparently create a transaction entry"""
        manage_addBLEntry(txn, self, amount, title)

    def manage_payAccount(self, amount, reference='', other_account=None, REQUEST=None):
        """
        make a physical funds payment on the account, implemented using
        BastionBanking

        Note this is intended to work polymorphically across all accounts in
        all types of ledger.
        """
        bms = self.getBastionMerchantService()

        if not bms:
            raise ValueError, 'No BastionMerchantService'
        
        # other account should be blank only in Ledger
        if not other_account:
            other_account = self.accountsForTag('bank_account')[0]

        txn = self.createTransaction('Payment')
        amount = abs(amount)
        if self.balance():
            other_account.createEntry(txn, amount, 'Cash')
            self.createEntry(txn,  -amount, 'Payment - Thank You')
        else:
            other_account.createEntry(txn, -amount, 'Cash')
            self.createEntry(txn, amount, 'Payment - Thank You')

        # if the merchant service redirects, we need to ensure the transaction remains ...
        transaction.get().commit()
        
        rc = bms.manage_payTransaction(txn, 
                                       reference,
                                       REQUEST=self.REQUEST)

        # BastionMerchantService may hihack us - redirecting our client ...
        if rc and REQUEST:
            REQUEST.set('Payment Processed')
            return self.manage_main(self, REQUEST)


    def manage_statusModify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        self.content_status_modify(workflow_action)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)
        
    def objectItemsByDate(self, meta_type=None, effective=None):
        """
        return list of entries in descending effective_date order, taking care to include
        any control account entries
        """
        obs = []
        effective = effective or DateTime()

        if type(effective) in (types.ListType, types.TupleType):
            if len(effective) > 1:
                dt_min = floor_date(min(effective))
                dt_max = ceiling_date(max(effective))
            else:
                dt_min = EPOCH
                dt_max = ceiling_date(max(effective))
        else:
            dt_min = EPOCH
            dt_max = effective
            
        for k, v in self.objectItems(meta_type):
            try:
                item_dt = v.effective()
            except:
                # hmmm - not a BLEntry ...
                raise
                
            LOG.error('doing (%s, %s) %s' % (dt_min, dt_max, str(v))) 
            if item_dt is None or (item_dt >= dt_min and item_dt <= dt_max):
                obs.append((k,v))

        obs.sort(lambda x,y: cmp(x[1], y[1]))
        return obs

    # need to allow setting of properties from Python Scripts...- maybe we should just
    # use manae_changeProperties ...
    def updateProperty(self, name, value):
        """
        set or update a property
        """
        if not self.hasProperty(name):
            self._setProperty(name, value)
        else:
            self._updateProperty(name, value)

    def sum(self, id, effective=[], debits=True, credits=True):
        """
        summate entries based upon id (the other account id), date range, and sign
        """
        if type(effective) not in (types.ListType, types.TupleType):
            if isinstance(effective, DateTime):
                effective = [EPOCH, effective]
            else:
                raise SyntaxError, 'incorrect parameter date!'
        currency = self.base_currency
        amount = ZCurrency(currency, 0)
        for entry in self.entryValues(effective):
            try:
                a = entry.blTransaction().entry(id).amountAs(currency)
            except:
                continue
            if (debits and a > 0) or (credits and a < 0):
                amount += a
        return amount

    def balances(self, dates, format='%0.2f'):
        """
        return string balance information for a date range (suitable for graphing)
        """
        return map(lambda x: self.balance(effective=x).strfcur(format), dates)

    def zeroAmount(self, currency=''):
        """
        a zero-valued amount in the currency of the account
        """
        return ZCurrency(currency or self.base_currency, 0)

    def allTags(self):
        """
        return a list of all the tags this account is associated with
        """
        tags = list(self.tags)
        pt = getToolByName(self, 'portal_bastionledger')
        ledger_id = self.aq_parent.getId()

        for assocs in pt.objectValues('BLAssociationFolder'):
            for tag in map(lambda x: x.getId(),
                           assocs.searchObjects(ledger=ledger_id, accno=self.accno)):
                if tag not in tags:
                    tags.append(tag)

        tags.sort()
        return tags

    def hasTag(self, tag):
        """
        """
        if tag in self.tags:
            return True

        pt = getToolByName(self, 'portal_bastionledger')
        for assocs in pt.objectValues('BLAssociationFolder'):
            if assocs.searchResults(ledger=self.aq_parent.getId(), accno=self.accno):
                return True

        return False

    def __cmp__(self, other):
        """
        hmmm - sorted based on accno
        """
        if not isinstance(other, BLAccount):
            return 1
        if other.accno > self.accno:
            return 1
        elif other.accno < self.accno:
            return -1
        return 0

    def __str__(self):
        return "<%s instance - (%s/%s [%s], %s)>" % (self.meta_type,
                                                     self.aq_parent.getId(),
                                                     self.getId(),
                                                     self.title,
                                                     self.balance())

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%a', REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt),
                             self.objectValues('BLEntry')))

    def getBastionMerchantService(self):
        """
        returns a Bastion Internet Merchant tool if present (or None) such that
        any/all account(s) could be paid-down via the internet
        """
        parent = self

        try:
            while parent:        
                bms = parent.objectValues('BastionMerchantService')
                if bms:
                    return bms[0]

                parent = parent.aq_parent
        except:
            pass

        return None

    def _repair(self):
        # remove BLObserverSupport
        for attr in ('onAdd', 'onChange', 'onDelete'):
            if getattr(aq_base(self), attr, None):
                delattr(self, attr)
        if not getattr(aq_base(self), 'tags', None):
            self.tags = []
	ledger_id = self.blLedger().getId()
        for entry in self.objectValues(['BLEntry', 'BLSubsidiaryEntry']):
	    if type(entry.ledger) != type(''):
		entry.ledger = ledger_id
            try:
                assert_currency(entry.amount)
            except:
                entry.amount = ZCurrency(entry.amount)
        if not getattr(aq_base(self), 'subtype', None):
            try:
                key = int(self.accno) / 100 * 100
                self.subtype = SUBTYPES.get(key, '')
            except:
                self.subtype = ''
	if self.__dict__.has_key('status'):
	    status = self.__dict__['status']
	    self._status(getToolByName(self, 'portal_workflow').getWorkflowsFor(self)[0].initial_state)
	    del self.__dict__['status']

        opening = getattr(aq_base(self), 'OPENING', None)
        if opening:
            delattr(self, 'OPENING')

        if getattr(aq_base(self), 'periods', None):
            delattr(self, 'periods')

        # force reindexing ...
        self.reindexObject()


AccessControl.class_init.InitializeClass(BLAccount)



class BLAccounts( BTreeFolder2, ZCatalog, PropertyManager ):
    """
    Specialised catalog for accounts 
    """

    meta_type = 'BLAccounts'

    __ac_permissions__ = BTreeFolder2.__ac_permissions__ + \
                         ZCatalog.__ac_permissions__ + \
                         PropertyManager.__ac_permissions__
        
    manage_options = ZCatalog.manage_options


    def __init__(self, id, title='', account_types=['BLAccount']):
        BTreeFolder2.__init__(self, id)
        ZCatalog.__init__(self, id, title)
        self.account_types = account_types
        self.addIndex('tags', 'KeywordIndex')
        self.addIndex('type', 'FieldIndex')
        self.addIndex('subtype', 'FieldIndex')
        self.addIndex('title', 'FieldIndex')
        self.addIndex('accno', 'FieldIndex')
        self.addIndex('status', 'FieldIndex')
        self.addIndex('meta_type', 'FieldIndex')
        self.addIndex('CreationDate', 'DateIndex')
        self.addColumn('id')
        self.addColumn('title')
        self.addColumn('type')
        self.addColumn('subtype')
        self.addColumn('meta_type')

    def all_meta_types(self):
        return ()


    index_html = None

    def __len__(self):
        return len(self._catalog.indexes.get('accno', []))

    def __call__(self, REQUEST=None, *args, **kw):
        """
	returns a list of BLAccount (derivatives) meeting the search criteria,
        wrapping ZCatalog.searchResults(), excepting returning objects instead of brains ...
	"""
        return map(lambda x: x.getObject(),
                   self.searchResults(REQUEST,*args,**kw))

    # this function is used in manage_catalogView and needs to be reliable ...
    def searchResults(self, REQUEST=None, *args, **kw):
        """
	returns a list of BLAccount (derivatives) meeting the search criteria,
        wrapping ZCatalog.searchResults()
	"""
        return ZCatalog.searchResults(self, REQUEST=self.mungeCriteria(REQUEST, *args, **kw))

    def mungeCriteria(self, REQUEST=None, *args, **kw):
        """
        tweak the search
        """
        if REQUEST is not None:
            if type(REQUEST) == type({}):
                criteria = dict(REQUEST)
            else:
                criteria = dict(REQUEST.form)
        else:
            criteria = {}
        criteria.update(kw)
        # convert tags to accno for our 'global' associations
        if criteria.has_key('tags'):
            accnos = self.tags2accnos(criteria['tags'])
            if accnos:
                # hmmm - we need to remove tags kw as this is an AND query not an OR query
                local_accnos = map(lambda x: x.accno,
                                   map(lambda x: x.getObject(),
                                       ZCatalog.searchResults(self, tags=criteria['tags'])))
                if local_accnos:
                    accnos.extend(local_accnos)
                del criteria['tags']
                if criteria.has_key('accno'):
                    criteria['accno'].extend(accnos)
                else:
                    criteria['accno'] = accnos
        criteria['meta_type'] = self.aq_parent.account_types
        return criteria

    def tags2accnos(self, tags):
        """
        go get global accnos corresponding to the tags
        """
        if type(tags) == type(''):
            tags = [tags]

        accnos = []

        bltool = getToolByName(self, 'portal_bastionledger', None)
        if bltool:
            for associations in bltool.objectValues('BLAssociationFolder'):
                for tag in tags:
                    assoc = associations.get(tag)
                    if assoc:
                        accnos.extend(assoc.accno)
        return accnos

    def ZopeFindAndApply(self, obj, obj_ids=None, obj_metatypes=None,
                         obj_searchterm=None, obj_expr=None,
                         obj_mtime=None, obj_mspec=None,
                         obj_permission=None, obj_roles=None,
                         search_sub=0,
                         REQUEST=None, result=None, pre='',
                         apply_func=None, apply_path=''):
        """
        ZCatalog seems to be broken - probably something to do with lazy-mapping and
        BTreeFolder2
        """
        for acc in filter(lambda x: isinstance(x, BLAccount), self.aq_parent.objectValues()):
            for entry in acc.entryValues():
                url = '/'.join(entry.getPhysicalPath())
                self.catalog_object(entry, url)
            url = '/'.join(acc.getPhysicalPath())
            self.catalog_object(acc, url)
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _repair(self):
        # need to delegate here because this is not a containment relationship ...
        if not getattr(aq_base(self), '_catalog', None):
            ZCatalog.__init__(self, self.getId(), self.title)
        try:
            self.addIndex('tags', 'KeywordIndex')
        except:
            pass
        try:
            self.addIndex('type', 'FieldIndex')
            self.addIndex('subtype', 'FieldIndex')
        except:
            # it's already there ...
            pass
        try:
            self.addColumn('type')
            self.addColumn('subtype')
        except:
            pass
        try:
            self.addColumn('meta_type')
        except:
            pass
        try:
            self.addIndex('status', 'FieldIndex')
        except:
            # it's already there ...
            pass
        try:
            self.addIndex('meta_type', 'FieldIndex')
        except:
            # it's already there ...
            pass
        for name in ('accno', 'title',):
            try:
                self.addIndex(name, 'FieldIndex')
            except:
                pass
        try:
            self.addIndex('CreationDate', 'DateIndex')
        except:
            pass

    def manage_repair(self, REQUEST=None):
        """
        """
        self._repair()
        if REQUEST:
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLAccounts)

def accno_field_cmp(x, y):
    if x.accno == y.accno: return 0
    if x.accno > y.accno: return 1
    return -1


def date_field_cmp(x, y):
    # we could have dangling accounts :(
    try:
        x_dt = x[1].effective()
    except:
        x_dt = EPOCH
    try:
        y_dt = y[1].effective()
    except:
        y_dt = ZERO_DATE
    if x_dt == y_dt: return 0
    if x_dt > y_dt: return 1
    return -1

