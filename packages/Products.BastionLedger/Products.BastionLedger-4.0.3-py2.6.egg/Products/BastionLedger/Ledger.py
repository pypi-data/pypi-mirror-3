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
import AccessControl, logging, os, types
from AccessControl.Permissions import view_management_screens, access_contents_information
from DateTime import DateTime, Timezones
from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.ObjectManager import REPLACEABLE
from OFS.PropertyManager import PropertyManager
from DocumentTemplate.DT_Util import html_quote
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
#
# get our local sub-helpers ...
#
from BLBase import *
from BLLedger import LedgerBase
from BLInventory import BLInventory
from BLOrderBook import BLOrderBook
from BLSubsidiaryLedger import BLSubsidiaryLedger
from BLShareholderLedger import BLShareholderLedger
from BLQuoteManager import BLQuoteManager

#
# Payroll is moving to a separate framework
#
try:
    from BLPayroll import BLPayroll
    DO_PAYROLL = True
except:
    DO_PAYROLL = False
from BLReport import BLReportFolder
from BLPeriodInfo import BLLedgerPeriodsFolder
from BLTransaction import manage_addBLTransaction
from BLEntry import manage_addBLEntry
from BLGlobals import EPOCH
from utils import ceiling_date, floor_date
from Permissions import OperateBastionLedgers, ManageBastionLedgers, GodAccess
from Exceptions import PostingError, MissingAssociation, UnbalancedError
from interfaces.tools import IBLLedgerTool, IBLLedgerToolMultiple

from zope.interface import Interface, implements

class ILedger(Interface): pass

manage_addLedgerForm = PageTemplateFile('zpt/add_Ledger', globals())

def manage_addLedger(self, id, title='', currency='', REQUEST=None, submit=None):
    """ adds a ledger """
    if not currency:
        currency = getToolByName(self, 'portal_bastionledger').Ledger.defaultCurrency()

    self._setObject(id, Ledger(id, title, 'Default', 666, currency))

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))
        
    return self._getOb(id)


def addBastionLedger(self, id, title=''):
    """
    Plone add ledger
    """
    ledger = manage_addLedger(self, id, title)
    return id

def attrCompare(x, y, attr):
    """
    compare named attribute from objects x and y
    """
    x_attr = getattr(x, attr)
    y_attr = getattr(y, attr)

    if callable(x_attr):
        x_attr = x_attr()
    if callable(y_attr):
        y_attr = y_attr()

    if x_attr > y_attr:
        return 1
    if x_attr < y_attr:
        return -1

    return 0

class Ledger(BObjectManager, PropertyManager, BSimpleItem):
    """
    The Accountancy offering.

    This class is a container for other BastionLedger sub-products and
    the chart of accounts.
    """
    implements(ILedger)
    
    __replaceable__ = REPLACEABLE
    dontAllowCopyAndPaste = 0
    meta_type = portal_type = 'Ledger'
    default_page = 'folder_listing'
    _reserved_names = ('Ledger', )
    timezone = 'UTC'
    industry_code = ''

    __ac_permissions__ = BObjectManager.__ac_permissions__ + (
        (access_contents_information, ('zeroAmount', 'ledgerLocalizedTime', 'inventoryValues', 
                                       'ledgerValues', 'transactionValues', 'entryValues', 'accountValues',
                                       'defaultCurrency', 'uniqueTransactionValues', 'emailAddress')),
        (View, ('gross_profit', 'losses_attributable', 'net_profit', 'corporation_tax',
                'profit_loss_acc', 'accrued_income_tax_acc', 'bastionLedger',
                'manage_downloadCSV', 'getLedgerProperty', 'directorInfo', 'secretaryInfo')),
        (view_management_screens, ('manage_edit', 'ledger_id', 'manage_periods', 'manage_reports',
                                   'manage_verify', 'verifyExceptions')),
        (GodAccess, ('manage_reset',)),
        (OperateBastionLedgers, ('manage_navigationIndex', 'moveTransaction')),
        (ManageBastionLedgers, ('manage_periodEnd', 'manage_periodEndReports', 'manage_recalculateControls',
                                'manage_refreshCatalog', 'manage_replaceLedger', 'manage_fixupCatalogs',
                                'manage_resetPeriods', 'manage_verifyRepost')),
    ) + PropertyManager.__ac_permissions__ + BSimpleItem.__ac_permissions__

    property_extensible_schema__ = 1
    _properties = (
	 { 'id':'title',              'type':'string', 'mode':'w' },
         { 'id':'company_number',     'type':'string', 'mode':'w' },
         { 'id':'incorporation_date', 'type':'date',   'mode':'w' },
         { 'id':'address',            'type':'text',   'mode':'w' },
         { 'id':'directors',          'type':'lines',  'mode':'w' },
         { 'id':'secretary',          'type':'string', 'mode':'w' },
         { 'id':'tax_number',         'type':'string', 'mode':'w' },
         { 'id':'industry_code',      'type':'string', 'mode':'w' },
         { 'id':'currency',           'type':'string', 'mode':'r' },
         { 'id':'timezone',           'type':'selection', 'mode':'w',
           'select_variable': 'TimeZones'},
         { 'id':'unique_identifier',  'type':'string', 'mode':'r' },
    )
                    
    manage_options =  (
        {'label': 'Contents',       'action':'manage_main',
         'help':('BastionLedger', 'system.stx')  }, 
        {'label': 'View',           'action':''},
        {'label': 'Properties',     'action': 'manage_propertiesForm',
         'help':('BastionLedger', 'system_props.stx') },
        {'label': 'Verify',         'action':'manage_verify' },
        {'label': 'Balance Sheet',  'action': 'blbalance_sheet' },
        {'label': 'Revenue Stmt',   'action':'blrevenue_statement'},
        {'label': 'Cashflow Stmt',  'action':'blcashflow_statement'},
        {'label': 'Periods',        'action':'manage_periods'},
        {'label': 'Reports',        'action':'manage_reports'},
        ) + BSimpleItem.manage_options

    manage_verify = PageTemplateFile('zpt/verify_ledger', globals())
    
    #
    # this needs lots more thought ...
    #
    #manage_sync = PageTemplateFile('zpt/view_reports', globals())

    def __init__(self, id, title, locale_id, unique_id, currency='USD', timezone='UTC'):
        self.id = id
        self.title = title
        self._locale = locale_id
        self.currency = currency
        self.timezone = timezone
        self.unique_identifier = unique_id
        self.company_number = ''
        self.incorporation_date = ''
        self.address = ''
        self.tax_number = ''
        self.industry_code = ''
        self.directors = []
        self.secretary = ''
        self.Reports = BLReportFolder('Reports')
        self.periods = BLLedgerPeriodsFolder()

    def displayContentsTab(self):
        """ 
        we don't catalog ledgers etc so folder_contents is incomplete
        """
        return False

        
    def manage_editProperties(self, REQUEST):
        """ correctly handle redirect """
        PropertyManager.manage_editProperties(self, REQUEST)
        REQUEST.set('manage_tabs_message', 'Updated')
        REQUEST.set('management_view', 'Properties')
        return self.manage_propertiesForm(self, REQUEST)

    def manage_reports(self, REQUEST, RESPONSE):
        """
        goto reports folder
        """
        RESPONSE.redirect('Reports/manage_workspace')

    def manage_periods(self, REQUEST, RESPONSE):
        """
        goto periods folders
        """
        RESPONSE.redirect('periods/manage_workspace')

    def manage_recalculateControls(self, effective=None, REQUEST=None):
        """
        """
        for subsidiary in filter(lambda x: isinstance(x, BLSubsidiaryLedger),
                                 self.objectValues()):
            subsidiary.manage_recalculateControl(effective or DateTime())
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Recalculated control accounts')
            return self.manage_main(self, REQUEST)

    def manage_replaceLedger(self, REQUEST=None):
        """
        If you set up a ledger via a different portal_bastionledger, you may want to
        recreate your Ledger with new currency and accounts - this function does that
        """
        txns = 0
        for ledger in self.ledgerValues():
            txns += len(ledger.transactionIds())

        if txns != 0:
            msg = 'There are %i transactions in your BastionLedger, you cannot replace it' % txns
            if REQUEST:
                REQUEST.set('manage_tabs_message', msg)
                return self.manage_main(self, REQUEST)
            raise ValueError, msg

        self._delObject('Ledger')

        #
        # copy stuff from our (new) global locale repository ...
        #
        locale = getToolByName(self, 'portal_bastionledger')

        ledger = locale.Ledger._getCopy(self)
        ledger._setId('Ledger')
        self._setObject('Ledger', ledger)
        ledger = self._getOb('Ledger')
        ledger._postCopy(self)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Replaced Ledger')
            return self.manage_main(self, REQUEST)

    def edit(self, title, description, company_number, incorporation_date,
             address, directors,secretary,tax_number, industry_code, currency, timezone):
        """ plone property edit """
        self.title = title
        self.description = description
        self.company_number = company_number
        self.incorporation_date = incorporation_date
        self.address = address
        self.directors = directors
        self.secretary = secretary
        self.tax_number = tax_number
        self.industry_code = industry_code
        self.currency = currency
        self.timezone = timezone
        

    def manage_edit(self, title, currencies=[], REQUEST=None):
        """ """
        self.title = title
        self.currencies = currencies
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def ledger_id(self):
        return self.unique_identifier

    def ledgerLocalizedTime(self, dt, long_format=None):
        """
        return a timezone-corrected date
        """
        if not isinstance(dt, DateTime):
            dt = DateTime(dt)
        return self.toLocalizedTime(dt.toZone(self.timezone), long_format)

    def _memberInfo(self, memberids):
        """
        """
        infos = []
        mt = getToolByName(self, 'portal_membership')
        for director in memberids:
            if director.find(' ') == -1:
                member = mt.getMemberById(director)
                if member:
                    infos.append({'id': director,
                                  'member': member})
                    continue
            infos.append({'id': director,
                          'member': None})
        return infos

    def directorInfo(self):
        """
        return a tuple of hashes of id, member with member info of any director id
        """
        return self._memberInfo(self.directors)

    def secretaryInfo(self):
        """
        """
        if self.secretary:
            return self._memberInfo([self.secretary])
        return []

    def getLedgerProperty(self, prop, default=''):
        """
        allow sub-objects to acquire our properties
        """
        return self.getProperty(prop, default)

    def bastionLedger(self):
        """
        return the BastionLedger toplevel instance
        """
        return self

    def zeroAmount(self):
        return ZCurrency('%s 0.00' % self.currency)

    def ledgerValues(self):
        """
        return a list of things that are ledgers ...
        """
        return filter(lambda x: isinstance(x, LedgerBase), self.objectValues())

    def inventoryValues(self):
        """
        return a list of inventories
        """
        return self.objectValues('BLInventory')

    def ledgerIds(self):
        """
        return id's of all ledgers
        """
        return map(lambda x: x.getId(), self.ledgerValues())

    def accountValues(self, REQUEST=None, **kw):
        """
        return all the accounts - if you pass kw, it does a catalog search
        """
        results = []
        for ledger in self.ledgerValues():
            results.extend(ledger.accountValues(REQUEST, **kw))

        if REQUEST or kw:
            sort_on = REQUEST and REQUEST.get('sort_on', '') or kw and kw.get('sort_on', '')
            if sort_on:
                results.sort(lambda x,y,sort_on=sort_on: attrCompare(x,y,sort_on))

        return results
                        

    def transactionValues(self, REQUEST={}, **kw):
        """
        return all the transactions - if you pass kw, it does a catalog search
        """
        results = []
        for ledger in self.ledgerValues():
            results.extend(ledger.transactionValues(REQUEST, **kw))

        if REQUEST or kw:
            sort_on = REQUEST.get('sort_on', kw.get('sort_on', ''))
            if sort_on:
                results.sort(lambda x,y,sort_on=sort_on: attrCompare(x,y,sort_on))

        return results
                        
    def uniqueTransactionValues(self, ndx):
        """
        get unique values for all Transaction indexes
        """
        results = []
        for ledger in self.ledgerValues():
            for v in ledger.uniqueTransactionValues(ndx):
                if v not in results:
                    results.append(v)
        results.sort()
        return results
        
    def entryValues(self, REQUEST=None, **kw):
        """
        return all the entries - if you pass kw, it does a catalog search,
        sort order is as per txn sorting
        """
        results = []
        for txn in self.transactionValues(REQUEST, **kw):
            results.extend(txn.entryValues())
        return tuple(results)

    def defaultCurrency(self):
        """
        """
        return self.currency

    def all_meta_types(self):
        """
        decide what's addable via our IBLLedgerTool/Multiple interfaces
        """
        instances = filter(lambda x: x.get('instance', None), Products.meta_types)

        multiples = filter(lambda x: IBLLedgerToolMultiple.implementedBy(x['instance']), instances)
        singletons = filter(lambda x: IBLLedgerTool.implementedBy(x['instance']), instances)

        if type(singletons) != types.TupleType:
            singletons = tuple(singletons)

        existing = map(lambda y: y.meta_type, self.objectValues())

        return filter( lambda x: x['name'] not in existing, singletons ) + multiples

    def expertMode(self):
        """
        returns whether or not all of the integrity constraints can be
        ignored because we're trying to perform some kind of remediation
        """
        try:
            return self.blledger_expert_mode()
        except:
            return False

    def TimeZones(self):
        """
        A list of available timezones for this ledger's effective
        dating mechanisms
        """
        return Timezones()

    def Currencies(self):
        """
        A list of available currencies for this ledger
        """
        return CURRENCIES
    
    def moveTransaction(self, tid, ledgerid, accno, entryid, REQUEST=None):
        """
        move a transaction from the GL to a subsidiary ledger account
        """
        # TODO - make it move subsidiary txn's as well ...
        # TODO - some enforcement
        txn = self.Ledger._getOb(tid)
        ledger = self._getOb(ledgerid)
        account = ledger._getOb(accno)

        new_txn = ledger.createTransaction(txn.effective(), title=txn.title)
        for entry in txn.entryValues():
            if entry.getId() == entryid:
                new_txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(accno, entry.amount, entry.title)
            else:
                l,acc = entry.account.split('/')
                new_txn.manage_addProduct['BastionLedger'].manage_addBLEntry(acc, entry.amount, entry.title)

        if len(new_txn.objectValues('BLSubsidiaryEntry')) != 1:
            raise PostingError, new_txn

        # this should be postable...
        new_txn.manage_post()

        # remove/reverse old txn
        self.Ledger.manage_delObjects([tid])

        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/manage_main' % new_txn.absolute_url())

    def manage_fixupCatalogs(self, REQUEST=None):
        """
        reload/repair catalogs
        """
        for ob in self.objectValues():
            if isinstance(ob, LedgerBase):
                ob.Accounts.manage_catalogClear()
                ob.Accounts.ZopeFindAndApply(ob,
                                             obj_metatypes=['BLAccount', 'BLSubsidiaryAccount',
                                                            'BLShareholder', 'BLEmployee',
                                                            'BLOrderAccount', 'BLEntry',
                                                            'BLSubsidiaryEntry'],
                                             search_sub=0,
                                             apply_path='/'.join(ob.getPhysicalPath()),
                                             apply_func=ob.Accounts.catalog_object)
                ob.Transactions.manage_catalogClear()
                ob.Transactions.ZopeFindAndApply(ob,
                                                 obj_metatypes=['BLTransaction',
                                                                'BLSubsidiaryTransaction'],
                                                 search_sub=0,
                                                 apply_path='/'.join(ob.getPhysicalPath()),
                                                 apply_func=ob.Transactions.catalog_object)
            if isinstance(ob, BLInventory):
                ob.catalog.manage_catalogClear()
                ob.catalog.ZopeFindAndApply(ob,
                                            obj_metatypes=['BLPart', 'BLPartFolder'],
                                            search_sub=1,
                                            apply_path='/'.join(ob.getPhysicalPath()),
                                            apply_func=ob.catalog.catalog_object)
                dispatcher = ob.dispatcher
                dispatcher.manage_catalogClear()
                dispatcher.ZopeFindAndApply(ob,
                                            obj_metatypes=['BLDispatchable'],
                                            search_sub=1,
                                            apply_path='/'.join(dispatcher.getPhysicalPath()),
                                            apply_func=dispatcher.catalog_object)
            if isinstance(ob, BLQuoteManager):
                ob.manage_catalogClear()
                ob.ZopeFindAndApply(ob,
                                    obj_metatypes=['BLQuote'],
                                    search_sub=1,
                                    apply_path='/'.join(ob.getPhysicalPath()),
                                    apply_func=ob.catalog_object)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Recataloged Ledger')
            return self.manage_main(self, REQUEST)

    def manage_reset(self, REQUEST=None):
        """
        clear down the entire ledger - useful after setting up your ledger and running a
        few test transactions proving it
        """
        # reset all the subsidiaries
        for ob in filter(lambda x: x.getId() != 'Ledger', self.ledgerValues()):
            ob._reset()
        # then reset the ledger
        self.Ledger._reset()
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reset Ledger!')
            return self.manage_main(self, REQUEST)

    def verifyExceptions(self, bothways=True, forcefx=False):
        """
        return a list of exceptions discovered (ie a tuple of exception name, entry, note)
        """
        bad_entries = []
        # first go check that all transactions posted properly
        for ledger in self.ledgerValues():
            for txn in ledger.transactionValues():
                bad_entries.extend(txn.manage_verify())

        if bothways:
            # then go check that there are no other entries in any of the accounts that
            # weren't in one of the above transactions ...
            
            for ledger in self.ledgerValues():
                for account in ledger.accountValues():
                    bad_entries.extend(account.manage_verify())

        if bad_entries:
            # exception class, entry, note/description
            return map(lambda x: (x[0].__class__.__name__, x[0].args[0], x[1]), bad_entries)

        
    def manage_verifyRepost(self, ids, force=False, REQUEST=None):
        """
        ids are txn paths, instantiate and repost them
        """
        count = 0
        root = self.getPhysicalRoot()
        for path in ids:
            txn = root.unrestrictedTraverse(path)
            txn.manage_repost(force=force)
            count += 1

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reposted %i transactions' % count)
            return self.manage_verify(self, REQUEST)

    def manage_inspect(self, REQUEST):
        """
        we've changed lots of underlying attributes - we can peak under the hood
        with this method
        """
        # we should really extend and format this very nicely - we could use this as
        # a user-based help tool ...
        keys = self.__dict__.keys()
        keys.sort
        output = []
        for k in keys:
            try:
                output.append('<tr><td>%s</td><td>%s</td></tr>' % (k, self.__dict__[k]))
            except Exception, e:
                output.append('<tr><td>%s</td><td>%s</td></tr>' % (k, str(e)))

        REQUEST.RESPONSE.write('<table>%s</table>' % ''.join(output))

    def _catalogApply(self, fn, args=(), kw={}):
        """
        helper driver to do stuff to *all* the underlying catalog's
        """
        for ledger in filter(lambda x: isinstance(x, LedgerBase), self.objectValues()):
            apply(ledger.Transactions, function, args, kw)
            apply(ledger.Accounts, function, args, kw)

    #
    # range of useful reporting functions ...
    #

    def gross_profit(self, effective=None, REQUEST=None):
        """
        report R - E for period indicated
        """
        effective = effective or DateTime().toZone(self.timezone)
        return -self.Ledger.sum(type=['Income', 'Expense'],
                                effective=effective)
    
    def losses_attributable(self, effective=None, gross_profit=None, REQUEST=None):
        """
        capital and operating losses from previous periods able to be offset
        against income - note this prove jurisdiction-dependent with varying
        expiries on such.

        we also don't return more than can be applied against gross profit ...
        """
        effective = effective or DateTime().toZone(self.timezone)
        
        try:
            losses_forward = self.periods.periodForLedger('Ledger', effective).losses_forward
        except:
            losses_forward = 0

        if losses_forward > 0:
            # yep - we have losses ...
            if not gross_profit:
                gross_profit = self.gross_profit(effective)
            if gross_profit > 0:
                # this period *is* in profit so we can attribute a loss
                return min(losses_forward, abs(gross_profit))
        return self.zeroAmount()
                         

    def corporation_tax(self, effective=[], gross_profit=None, attributable_losses=None, REQUEST=None):
        """
        calculate the corporation tax payable over the period
        """
        effective = effective or [DateTime().toZone(self.timezone)]
        if not gross_profit:
            gross_profit = self.gross_profit(effective)
        if not attributable_losses:
            attributable_losses = self.losses_attributable(effective)
        if gross_profit > 0:
            btool = getToolByName(self, 'portal_bastionledger')
            company_tax = getattr(btool, 'company_tax', None)
            if company_tax:
                return company_tax.calculateTax(max(effective), gross_profit - attributable_losses)
        # eek a loss ...
        return self.zeroAmount()
    
    def net_profit(self, effective, gross_profit=None,
                   attributable_losses=None, corporation_tax=None, REQUEST=None):
        """
        calculate the net profit for the period
        """
        if not gross_profit:
            gross_profit = self.gross_profit(effective)
        if not attributable_losses:
            attributable_losses = self.losses_attributable(effective)
        if not corporation_tax:
            corporation_tax = self.corporation_tax(effective,
                                                   gross_profit,
                                                   attributable_losses)
        return gross_profit - attributable_losses - corporation_tax

    def profit_loss_acc(self):
        """
        return the ledger account for current earnings
        """
        try:
            return self.Ledger.accountsForTag('profit_loss')[0]
        except:
            raise MissingAssociation, 'profit_loss'
        
    def accrued_income_tax_acc(self):
        """
        return the ledger account to which we accrue corporation tax
        """
        try:
            return self.Ledger.accountsForTag('tax_accr')[0]
        except:
            raise MissingAssociation, 'tax_accr'


    def asCSV(self, datefmt='%Y/%m/%d', txns=True, REQUEST=None):
        """
        return comma-separated variables of the entries

        you can select alternative date and currency formats, and the txns flag
        selects between choosing the entries from the BLTransactions or the BLAccounts
        of the ledgers
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt, txns), self.ledgerValues()))

    def manage_downloadCSV(self, REQUEST, RESPONSE, datefmt='%Y/%m/%d', txns=True):
        """
        a comma-separated list of *all* transaction entries, suitable for loading into Excel etc
        """
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.csv' % self.getId().lower())
        RESPONSE.write(self.asCSV(datefmt, txns))

    def manage_resetPeriods(self, REQUEST=None):
        """
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        pt.manage_reset(self)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reset periods')
            return self.manage_main(self, REQUEST)
        

    def manage_periodEnd(self, effective, force=False, REQUEST=None):
        """
        hmmm - this needs a complex REQUEST in order to pass arguments to ledger
        period-ends ....
        """
        pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
        pt.manage_periodEnd(self, effective, force)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Done period end for %s' % effective)
            return self.manage_main(self, REQUEST)

    def manage_periodEndReports(self, effective, REQUEST=None):
        """
        hmmm - this needs a complex REQUEST in order to pass arguments to ledger
        period-ends ....

        effective is now the period-id date ...
        """
        if not isinstance(effective, DateTime):
            effective = DateTime(effective)

        timezone = self.timezone
        if not effective.timezone() == timezone:
            effective = effective.toZone(timezone)

        effective = floor_date(effective)
        periods = self.periods.objectValues('BLPeriodInfos')

        if effective in map(lambda x: x.effective(), periods):
            pinfoid = filter(lambda x: x.effective() == effective, periods)[0].getId()
            pt = getattr(getToolByName(self, 'portal_bastionledger'), 'periodend_tool')
            pt.manage_generateReports(self, pinfoid, effective)
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Done period end reports for %s' % effective)
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No period-end run for %s' % effective)
            else:
                raise ValueError, 'No period-end run for: %s' % effective
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_refreshCatalog(self, clear=1, REQUEST=None):
        """
        go and reindex *everything*
        """
        for ledger in self.ledgerValues():
            ledger.Transactions.refreshCatalog(clear=clear)
            ledger.Accounts.refreshCatalog(clear=clear)

        for inventory in self.objectValues('BLInventory'):
            inventory.catalog.refreshCatalog(clear=clear)
            inventory.dispatcher.refreshCatalog(clear=clear)

        for quotemgr in self.objectValues('BLQuoteManager'):
            quotemgr.refreshCatalog(clear=clear)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'refreshed catalogs')
            return self.manage_main(self, REQUEST)

    def manage_resetProperties(self, REQUEST=None):
        """
        """
        if getattr(aq_base(self),'_properties', None):
            try:
                delattr(self, '_properties')
            except:
                pass
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_navigationIndex(self, REQUEST=None):
        """
        ensure all these first-level objects are available to the navigation portlet
        """
        cat = getToolByName(self, 'portal_catalog', None)
        count = 0
        if cat:
            for ob in self.objectValues():
                url = '/'.join(ob.getPhysicalPath())
                cat.uncatalog_object(url)
                cat.catalog_object(ob, url)
                count += 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Cataloged %i items' % count)
            return self.manage_main(self, REQUEST)


    def _repair(self):

        # hmmm - convert crap DateRangeIndex to DateIndex ...

        for ledger in self.ledgerValues():
            dt_ndx = ledger.Transactions._catalog.getIndex('effective_date')
            if dt_ndx.meta_type != 'DateIndex':
                ledger.Transactions.manage_delIndex(['effective_date'])
                ledger.Transactions.manage_addIndex('effective_date', 'DateIndex')
                ledger.Transactions.manage_reindexIndex(['effective_date'])

        # hmmm fix up effective date's on control entries
        #from BLSubsidiaryLedger import BLSubsidiaryLedger
        #for sub in filter(lambda x: isinstance(x, BLSubsidiaryLedger), self.objectValues()):
        #    # ensure a control entry is present ...
        #    sub.manage_recalculateControl()
        #    controlEntry = sub.controlEntry()
        #    if not controlEntry.effective_date():
        #        controlEntry._setEffectiveDate(sub.CreationDate())

        # hmmm - revert historicals stuff
        if getattr(aq_base(self), 'historicals', None):
            for ledger in self.historicals.objectValues():
                properledger = self._getOb(ledger.getId())
                for txn in ledger.transactionValues():
                    id = txn.getId()
                    if not getattr(aq_base(properledger), id, None):
                        properledger._setObject(id, txn._getCopy(properledger))
                    properledger._getOb(id).manage_repost()

            delattr(self, 'historicals')

        # ok do the Accounts/Transactions migration ...
        for ledger in self.ledgerValues():
            #ledger.migrateAccountsTransactions()
            for account in ledger.accountValues():
                # convert opening balances
                try:
                    account._delOb('OPENING')
                except:
                    pass
                # fix bad paths
                for entry in account.entryValues():
                    entry._repair()
            ledger._repair()  # ensure indexes

        # remove local associations
        bltool = getToolByName(self, 'portal_bastionledger', None)
        if bltool:
            global_tags = bltool.associations.objectIds() 
            for account in self.Ledger.accountValues():
                tags = list(account.tags)
                reindex = False
                for tag in tags:
                    if tag in global_tags:
                        tags.remove(tag)
                        reindex = True
                if reindex:
                    try:
                        account._updateProperty('tags', tags)
                    except: # BadRequest
                        #account._setProperty('tags', tags, 'lines')
                        # hmmm - this is one where the properties have got ZODB persisted - most
                        # probably to add a 'rate' or something ...
                        delattr(account, '_properties')
                        account = self.Ledger._getOb(account.getId())
                        account._updateProperty('tags', tags)
                    account.reindexObject(idxs=['tags'])
        if not getattr(aq_base(self), 'Reports', None):
            self.Reports = BLReportFolder('Reports')
        if not getattr(aq_base(self), 'periods', None):
            self.periods = BLLedgerPeriodsFolder()

    def emailAddress(self):
        """
        return email address
        """
        # TODO 
        return ""
        
    def manage_emailStatement(self, email, sender, template, effective=None, REQUEST=None):
        """
        email a Revenue Statement, Balance Sheet, or Cashflow Statement to a recipient
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise ValueError, 'no MailHost found'
        
        # ensure 7-bit
        mail_text = str(getattr(self, template)(self, self.REQUEST, sender=sender, 
                                                email=email, effective=effective or DateTime()))

        mailhost._send(sender, email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Statement emailed to %s' % email)
            return self.manage_main(self, REQUEST)
        
AccessControl.class_init.InitializeClass(Ledger)


def addLedger(ob, event):
    #
    # if we're called from copy support/import, our catalog paths are probably borked ...
    #
    if getattr(aq_base(ob), 'Ledger', None):
        ob.manage_fixupCatalogs()
        return

    #
    # copy stuff from our global locale repository ...
    #
    locale = getToolByName(ob, 'portal_bastionledger')

    # hand-craft manage_clone because we don't all_meta_types BLLedger ...
    if not getattr(aq_base(ob), 'Ledger', None):
        try:
            ledger = locale.Ledger._getCopy(ob)
        except CopyError:
            # there is no _p_jar - this is still just a faux object in portal_factory
            return
        ledger._setId('Ledger')
        ob._setObject('Ledger', ledger)
    ledger = ob._getOb('Ledger')
    ledger._postCopy(ob)

    ob._setObject('Inventory', BLInventory('Inventory', 'Stock'))
    
    try:
        ob._setObject('Receivables',
                      BLOrderBook('Receivables', 'Customer Ledger',
                                  ledger.accountsForTag('receivables')[0],
                                  'Inventory', ledger.currencies, 'AR', 'A', 'AR'))
    except IndexError:
        raise MissingAssociation, 'receivables'
            
    try:
        ob._setObject('Payables',
                      BLOrderBook('Payables', 'Supplier Ledger',
                                  ledger.accountsForTag('payables')[0],
                                        'Inventory', ledger.currencies, 'AP', 'A', 'AP'))
    except IndexError:
        raise MissingAssociation, 'payables'
    
    try:
        ob._setObject('Shareholders',
                      BLShareholderLedger('Shareholders', 'Shareholders Ledger/Register',
                                          ledger.accountsForTag('shareholders')[0]))
    except IndexError:
        raise MissingAssociation, 'shareholders'

    if DO_PAYROLL:
        try:
            wages_and_salaries = ledger.accountsForTag('wages')[0]
            ob._setObject('Payroll',
                          BLPayroll('Payroll', 'Employee Payroll',
                                    wages_and_salaries, 'Friday', ledger.currencies))
        except IndexError:
            raise MissingAssociation, 'wages'

    # make sure Plone knows about these items ...
    ob.manage_navigationIndex()

from OFS.ObjectManager import BeforeDeleteException

def delLedger(ob, event):
    """
    hmmm - all our integrity constraints cause delete events to barf
    for non- expertMode users, so we commit suicide first to allow
    ourselves to be deleted normally
    """
    # hmmm - some old ledgers barf ...
    try:
        ob.manage_reset()
    except:
        pass
        
    # clean up any Plone stuff ...
    cat = getToolByName(ob, 'portal_catalog', None)
    if cat:
        for o in ob.objectValues():
            url = '/'.join(o.getPhysicalPath())
            try:
                cat.uncatalog_object(url)
            except:
                pass
