#
#    Copyright (C) 2008-2011  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, logging, os, operator, types
from Acquisition import aq_parent, aq_inner, aq_base
from DateTime import DateTime
from AccessControl.Permissions import view_management_screens, access_contents_information

import Products

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
from BLBase import BObjectManager as Folder, ProductsDictionary
from BLLedger import BLLedger
from BLAccount import manage_addBLAccount
from BLAssociations import manage_addBLAssociationsFolder, manage_addBLAssociation
from BLProcess import BLProcess
from BLTaxTables import BLTaxTable

from PeriodEndTool import manage_addPeriodEndTool
from DepreciationTool import manage_addDepreciationTool
import BLShareholderLedger
from BLPeriodInfo import BLLedgerPeriodsFolder

from Permissions import ManageBastionLedgers, OperateBastionLedgers
from utils import ceiling_date

from zope.interface import Interface, implements
from interfaces.tools import IBLControllerTool, IBLControllerToolMultiple

LOG = logging.getLogger('LedgerControllerTool')

class ILedgerControllerTool(Interface): pass

class LedgerControllerTool(UniqueObject, Folder, ActionProviderBase):
    """
    This tool provides group-wide jurisdiction-specific and other control
    data and processes across the BastionLedger's in your site.
    """

    implements(ILedgerControllerTool)

    id = 'portal_bastionledger'
    meta_type = 'BastionLedger Controller'
    portal_type = 'LedgerControllerTool'

    year_end = DateTime('2001/06/30')

    icon = 'misc_/BastionLedger/blcontroller'

    # stuff to keep Ledger views happy
    timezone = 'UTC'

    __ac_permissions__ = (
        (ManageBastionLedgers, ('manage_generateLedger',)),
        (ManagePortal, ('manage_overview',)),
        (OperateBastionLedgers, ( 'settlementAccount',)),
        (access_contents_information, ('processValues', 'processesForLedger','taxCodes', 'calculateTax',
                                       'hasTaxTable', 'currency', 'yearEnd', 
                                       'addCurrencies', 'convertCurrency', 'crossBuyRate', 'crossMidRate',
                                       'crossSellRate')),
        (view_management_screens, ('manage_ledger', 'Currencies')),
        ) + Folder.__ac_permissions__ + ActionProviderBase.__ac_permissions__

    _actions = ()

    # fudge so opening balances work for contained charts of accounts ...
    periods = BLLedgerPeriodsFolder()

    _properties = Folder._properties + (
        {'id':'year_end',       'type':'date',     'mode':'w'},
        )

    manage_overview = PageTemplateFile('zpt/controllertool_explain', globals())
    manage_ledger = PageTemplateFile('zpt/controller_ledger', globals())
    
    manage_options = ( Folder.manage_options[0], ) + ActionProviderBase.manage_options + (
        {'label':'Overview', 'action':'manage_overview'},
        {'label':'Ledger',   'action':'manage_ledger'},
        ) + Folder.manage_options[1:]

    def __init__(self, id='', title='BastionLedger policies tool'):
        self.title = title

    def all_meta_types(self):
        """
        decide what's addable via our IBLControllerTool/Multiple interfaces
        """
        instances = filter(lambda x: x.get('instance', None), Products.meta_types)

        multiples = filter(lambda x: IBLControllerToolMultiple.implementedBy(x['instance']), instances)
        singletons = filter(lambda x: IBLControllerTool.implementedBy(x['instance']), instances)

        if type(singletons) != types.TupleType:
            singletons = tuple(singletons)

        existing = map(lambda y: y.meta_type, self.objectValues())

        return filter( lambda x: x['name'] not in existing, singletons ) + multiples

    def Currencies(self):
        """
        return a list of available currencie codes
        """
        # these are the currencies which we've got SPOT rates for ...
        portal_currencies = getToolByName(self, 'portal_currencies', None)
        if portal_currencies:
            return portal_currencies.currencyCodes()
        return CURRENCIES

    def currency(self):
        """
        returns the currency all ledgers will be created with
        """
        # hmmm  defaultCurrency falls back to us ...
        #return self.Ledger.defaultCurrency()
        ledger = getattr(self, 'Ledger', None)
        if ledger:
            return ledger.currencies[0]
        # doh - no ledger ...
        return ''

    def convertCurrency(self, amount, effective, currency):
        """
        convert/price an amount to another currency
        """
        if amount.currency() != currency:
            if amount.amount():
                portal_currencies = getToolByName(self, 'portal_currencies', None)
                if not portal_currencies:
                    raise NotImplementedError, 'Currency conversion unavailable'

                rate = portal_currencies.crossMidRate(amount.currency(), currency, effective or DateTime())
                return ZCurrency(currency, amount.amount() * rate)
            else:
                return ZCurrency(currency, 0)
        return amount

    def crossBuyRate(self, currency1, currency2, effective=DateTime()):
        """
        return the buy-price of the currency cross rate for the day
        """
        if currency1 != currency2:
            portal_currencies = getToolByName(self, 'portal_currencies', None)
            if not portal_currencies:
                raise NotImplementedError, 'Currency conversion unavailable'
            
            return portal_currencies.crossBuyRate(currency1, currency2, effective)
        return 1.0

    def crossMidRate(self, currency1, currency2, effective=DateTime()):
        """
        return the mid-price of the currency cross rate for the day in the base of currency1
        """
        if currency1 != currency2:
            portal_currencies = getToolByName(self, 'portal_currencies', None)
            if not portal_currencies:
                raise NotImplementedError, 'Currency conversion unavailable'
            
            return portal_currencies.crossMidRate(currency1, currency2, effective)
        return 1.0

    def crossSellRate(self, currency1, currency2, effective=DateTime()):
        """
        return the sell-price of the currency cross rate for the day
        """
        if currency1 != currency2:
            portal_currencies = getToolByName(self, 'portal_currencies', None)
            if not portal_currencies:
                raise NotImplementedError, 'Currency conversion unavailable'
            
            return portal_currencies.crossSellRate(currency1, currency2, effective)
        return 1.0

    def addCurrencies(self, amounts, currency):
        """
        sum (and convert if necessary) a list of ZCurrency, DateTime tuples to specified
        currency
        """
        portal_currencies = getToolByName(self, 'portal_currencies', None)

        total = ZCurrency(currency, 0)

        try:
            for amt, effective in amounts:
                if amt.currency() != currency:
                    rate = portal_currencies.crossMidRate(amt.currency(), currency, ceiling_date(effective))
                    total += amt.amount() * rate
                else:
                    total += amt
        except:
            if not portal_currencies:
                raise NotImplementedError, 'Currency conversion unavailable'
            raise
            
        return total

    def manage_generateLedger(self, currency, chart, jurisdictions=[], REQUEST=None):
        """
        set up the default Ledger, along with the required association entries

        chart is the filesystem file with the chart CSV
        jurisdictions is a list of jurisdictions (ie jurisdiction + and sub-jurisdictions)
        """
        if getattr(aq_base(self), 'Ledger', None):
            self._delObject('Ledger')
            
        self._setObject('Ledger', BLLedger('Ledger', 'General Ledger', [ currency ]))
        ledger = self._getOb('Ledger')

        if not getattr(aq_base(self), 'associations', None):
            manage_addBLAssociationsFolder(self)
        associations = self.associations

        LOG.debug('populating accounts from file: %s' % chart)

        try:
            file = open(chart, 'r')  # TODO - we need unicode ...
        except IOError, e:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Unsupported chart: %s' % chart)
                return self.manage_main(self, REQUEST)
            raise IOError, '%s: %s' % (chart, str(e))

        for line in file.readlines():
            line = line.rstrip()
            number,name,typ,subtype,tags = line.split('|')
            if tags:
                tags=tags.split(',')
            else:
                tags=[]
            try:
                acct = manage_addBLAccount(ledger, name, currency, type=typ, subtype=subtype, accno=number)
                for tag in tags:
                    try:
                        assoc = associations._getOb(tag)
                    except (AttributeError, KeyError):
                        manage_addBLAssociation(associations, tag, 'Ledger', [number])
                        continue
                    assoc._updateProperty('accno', assoc.accno + (number,))
            except ValueError:
                raise ValueError, line
        
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Added Ledger for currency %s' % currency)
            return self.manage_main(self, REQUEST)

    def processesForLedger(self, ledger):
        """
        return a list of processes that can be run against the ledger, with the
        ledger in the acquisition context
        """
        return map(lambda x,ledger=ledger: x.aq_inner.__of__(ledger),
                   filter(lambda x,ledger=ledger: x.processFor(ledger),
                          self.processValues()))
    
    def processValues(self):
        """
        return a list of BLProcess-like objects
        """
        return filter(lambda x: isinstance(x, BLProcess),
                      self.objectValues())

    def taxCodes(self, effective=None):
        """
        return a list of all known tax codes
        """
        codes = []
        for table in self.objectValues('BLTaxTable'):
            codes.extend(table.taxCodes(effective))
        return codes

    def calculateTax(self, effective, amount, account, taxgrp=''):
        """
        for an account, figure out the taxes on an amount for a given
        effective date - we may defer to the tax table record
        to do sophisticated/custom processing (well - potentially
        sophisticated processing...)
        """
        tax = ZCurrency(amount.currency(), 0)

        if taxgrp:
            taxgroups = (taxgrp,)
        else:
            taxgroups = account.tax_codes.keys()
        
        for group in taxgroups:
            ttable = getattr(self, group, None)
            if ttable and isinstance(ttable, BLTaxTable):
                recs = ttable.getTableRecords(effective, amount=amount)
                codes = account.tax_codes[group]
                if codes:
                    recs = filter(lambda x:x.code in codes, recs)
                if recs:
                    tax += reduce(operator.add, map(lambda x,a=amount: x.tax(a), recs))

        return tax

    def taxAmount(self, effective, amount, account, taxgrp=''):
        """
        for an account, figure out the taxes inclued in an amount for a given
        effective date - we may defer to the tax table record
        to do sophisticated/custom processing (well - potentially
        sophisticated processing...)
        """
        tax = ZCurrency(amount.currency(), 0)

        if taxgrp:
            taxgroups = (taxgrp,)
        else:
            taxgroups = account.tax_codes.keys()
        
        for group in taxgroups:
            ttable = getattr(self, group, None)
            if ttable and isinstance(ttable, BLTaxTable):
                recs = ttable.getTableRecords(effective, amount=amount)
                codes = account.tax_codes[group]
                if codes:
                    recs = filter(lambda x:x.code in codes, recs)
                if recs:
                    tax += reduce(operator.add, map(lambda x,a=amount: x.taxIncluded(a), recs))

        return tax


    def hasTaxTable(self, id):
        return isinstance(getattr(aq_base(self), id, None), BLTaxTable)

    def settlementAccount(self, ledger, taxgrp):
        """
        figure out the settlement account for a tax table
        """
        # this implementation may change
        return ledger.accountsForTag(taxgrp)[0]
    
    def yearEnd(self, effective=DateTime()):
        """
        return the next year end day
        """
        year = effective.year()

        dt = DateTime('%i/%s/%s' % (year, self.year_end.month(), self.year_end.day()))

        if dt > effective:
            return dt

        return DateTime('%i/%s/%s' % (year + 1, self.year_end.month(), self.year_end.day()))

AccessControl.class_init.InitializeClass(LedgerControllerTool)


def addLedgerControllerTool(ob, event):

    # add our period-end processing functionality
    if not getattr(aq_base(ob), 'periodend_tool', None):
        manage_addPeriodEndTool(ob)

    # add our depreciation calculator
    if not getattr(aq_base(ob), 'depreciation_tool', None):
        manage_addDepreciationTool(ob)

    # load up all our processes
    if not getattr(aq_base(ob), 'dividend', None):
        ob._setObject('dividend',
                      BLShareholderLedger.BLDividendProcess('dividend', 'Dividend'))

