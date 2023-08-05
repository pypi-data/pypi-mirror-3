#
#    Copyright (C) 2007-2009  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, math, operator
from DateTime import DateTime
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from BLBase import *
from BLAttachmentSupport import BLAttachmentSupport
from Products.CMFCore import permissions
from Products.BastionBanking.ZCurrency import ZCurrency
from AccessControl.Permissions import view
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from BLEntry import manage_addBLEntry
from Exceptions import InvalidPeriodError, DepreciationError
from utils import floor_date, ceiling_date
from BLGlobals import EPOCH

from zope.interface import Interface, implements
from interfaces.tools import IBLLedgerToolMultiple


def saneDateRange(date_range, tz):
    # hmmm - calendar widget seems to be struggling ...
    clean_dates = []
    for dt in date_range:
        try:
            dt = DateTime(dt).toZone(tz)
        except:
            continue
        clean_dates.append(dt)
    return clean_dates

class BLAsset(PropertyManager, BLAttachmentSupport):
    """
    A record of a company asset
    """

    meta_type = portal_type = 'BLAsset'

    last_depreciation_run = EPOCH

    _properties = BLAttachmentSupport._properties + (
        {'id':'purchase_date',        'type':'date',     'mode':'w'},
        {'id':'purchase_price',       'type':'currency', 'mode':'w'},
        {'id':'improvement_costs',    'type':'currency', 'mode':'w'},
        {'id':'tax_credits',          'type':'currency', 'mode':'w'},
        {'id':'relief_credits',       'type':'currency', 'mode':'w'},
        {'id':'disposal_date',        'type':'date',     'mode':'w'},
        {'id':'disposal_price',       'type':'currency', 'mode':'w'},
        {'id':'depreciation_method',  'type':'selection','mode':'w',
         'select_variable': 'getDepreciationMethods'},
        {'id':'depreciation_to_date', 'type':'currency', 'mode':'w'},
        {'id':'last_depreciation_run','type':'date',     'mode':'w'},
        {'id':'asset_account',        'type':'selection', 'mode':'w',
         'select_variable': 'getAssetAccounts'},
        {'id':'percentage_owned',     'type':'float', 'mode':'w'},
        {'id':'effective_life',       'type':'float', 'mode':'w'},
        {'id':'percentage_rates',     'type':'lines', 'mode':'w'},
        )

    default_page = 'blasset_view'

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (view, ('depreciation', 'bookValue', 'terminationValue', 'totalCost', 'isDisposed')),
        (permissions.ModifyPortalContent, ('edit',)),
        ) + BLAttachmentSupport.__ac_permissions__

    manage_options = PropertyManager.manage_options + (
        {'label':'View', 'action':'' },
        ) + BLAttachmentSupport.manage_options

    def __init__(self, id, title, description, purchase_date, purchase_price,
                 asset_account, depreciation_method, effective_life, percentage_rates,
                 percentage_owned=100.0):
        zero = ZCurrency('%s 0.00' % purchase_price.currency())
        self.id = id
        self.title = title
        self.description = description
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.improvement_costs = zero
        self.tax_credits = zero
        self.relief_credits = zero
        self.disposal_date = EPOCH
        self.disposal_price = zero
        self.depreciation_to_date = zero
        self.depreciation_method = depreciation_method
        self.last_depreciation_run = EPOCH
        self.effective_life = effective_life
        self.percentage_rates = percentage_rates
        self.asset_account = asset_account
        self.percentage_owned = percentage_owned
        
    def edit(self, purchase_price, purchase_date, improvement_costs, tax_credits, relief_credits,
             disposal_date, disposal_price, depreciation_to_date, depreciation_method,
             effective_life, percentage_rates, asset_account, percentage_owned):
        """
        Plone edit function
        """
        self._updateProperty('purchase_price', purchase_price)
        self._updateProperty('purchase_date', purchase_date)
        self._updateProperty('improvement_costs', improvement_costs)
        self._updateProperty('tax_credits', tax_credits)
        self._updateProperty('relief_credits', relief_credits)
        self._updateProperty('disposal_date', disposal_date)
        self._updateProperty('disposal_price', disposal_price)
        self._updateProperty('depreciation_to_date', depreciation_to_date)
        self._updateProperty('depreciation_method', depreciation_method)
        self._updateProperty('effective_life', effective_life)
        self._updateProperty('percentage_rates', percentage_rates)
        self._updateProperty('asset_account', asset_account)
        self._updateProperty('percentage_owned', percentage_owned)
    
    def getAssetAccounts(self):
        return map(lambda x: x.getId(), self.aq_parent.asset_accounts())

    def getAssetAccount(self):
        try:
            return self.aq_parent.Ledger._getOb(self.asset_account)
        except:
            return None

    def getDepreciationMethods(self):
        return self.aq_parent.depreciation_methods() 

    def bookValue(self, effective=None):
        """
        how much the asset is worth on our books
        """
        if self.isDisposed():
            return self.zeroAmount()

        cost = self.totalCost()
        effective = effective or DateTime()

        #
        # it is important to be able to return a book value without recourse
        # to depreciation calculation - which may well recurse upon bookValue()
        #
        if effective == self.last_depreciation_run:
            bv = cost - self.depreciation_to_date
        elif effective > self.last_depreciation_run:
            bv = cost - self.depreciation_to_date - \
                self.depreciation((self.last_depreciation_run, effective))
        else:
            bv = cost - self.depreciation((self.purchase_date, effective))

        if bv > 0:
            return bv

        return self.zeroAmount()

    def terminationValue(self):
        """
        price at disposal adjusted for book value 
        """
        return self.disposal_price - self.bookValue()


    def _updateProperty(self, name, value):
        if name == 'percentage_rates':
            rates = []
            for rate in value:
                try:
                    rates.append(float(rate))
                except:
                    raise ValueError, 'not a percentages: %s' % rate
            value = rates
        PropertyManager._updateProperty(self, name, value)
                
    def isDisposed(self):
        """
        indicate whether or not the asset has been sold or otherwise disposed of
        """
        return self.disposal_date > EPOCH

    def depreciation(self, date_range, REQUEST=None):
        """
        return the total amount to depreciate for the specified period rage
        """
        date_range = saneDateRange(date_range, self.timezone)
        date_range = (floor_date(min(date_range)), ceiling_date(max(date_range)))
        amt = getattr(getToolByName(self, 'portal_bastionledger'),
                      'depreciation_tool').depreciationFunction(self.depreciation_method)(self, date_range)

        # don't allow more than book value to be written off ...
        residual = self.totalCost() - self.depreciation_to_date
        return min(amt, residual)
    
    def totalCost(self):
        return (self.purchase_price + self.improvement_costs - self.tax_credits \
                - self.relief_credits) * self.percentage_owned / 100

    def zeroAmount(self):
        return ZCurrency('%s 0.00' % self.purchase_price.currency())

AccessControl.class_init.InitializeClass(BLAsset)

manage_addBLAssetForm = PageTemplateFile('zpt/add_asset', globals())
def manage_addBLAsset(self, purchase_date, purchase_price, asset_account,
                      depreciation_method, effective_life, percentage_rates=[],
                      percentage_owned=100.0, title='', description='', id='',
                      REQUEST=None):
    """
    """
    id = id or self.generateId()
    self._setObject(id, BLAsset(id, title, description, purchase_date, purchase_price,
                                asset_account, depreciation_method, effective_life,
                                percentage_rates, percentage_owned))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' % (REQUEST['URL3'], id))
    return id


def addBLAsset(self, id='', title=''):
    """
    sucky Plone non-default params add
    """
    id = manage_addBLAsset(self,
                           DateTime(),
                           self.zeroAmount(),
                           self.asset_accounts()[0].getId(),
                           self.depreciation_methods()[0],
                           5,id=id,title=title)
    return id

manage_addBLAssetRegisterForm = PageTemplateFile('zpt/add_assetregister', globals())
def manage_addBLAssetRegister(self, id, title='', description='', REQUEST=None):
    """
    """
    self._setObject(id, BLAssetRegister(id, title, description))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))

class BLAssetRegister(BObjectManagerTree):
    """
    Store assets, compute depreciation and book values
    """
    meta_type = portal_type = 'BLAssetRegister'

    implements(IBLLedgerToolMultiple)


    manage_main = PageTemplateFile('zpt/assets_main', globals())
    manage_depreciation = PageTemplateFile('zpt/assets_depreciation', globals())
    manage_btree = BObjectManagerTree.manage_main

    default_page = 'blassetregister_view'
    
    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (ManageBastionLedgers, ('edit', 'manage_applyDepreciation', 'manage_reset')),
        (view_management_screens, ('manage_depreciation',)),
        )

    manage_options = (
        BObjectManagerTree.manage_options[0],
        {'label':'Depreciate', 'action':'manage_depreciation' },
        ) + BObjectManagerTree.manage_options[1:]

    _properties = BObjectManagerTree._properties + (
        {'id':'subtypes',     'mode':'w', 'type':'multiple selection',
         'select_variable':'getSubTypes'},
        {'id':'applied_from', 'mode':'r', 'type':'date'},
        {'id':'applied_to',   'mode':'r', 'type':'date'}
        )

    def __init__(self, id, title, description):
        BObjectManagerTree.__init__(self, id, title)
        self.description = description
        self.subtypes = [ 'Capital Assets' ]
        self.applied_from = EPOCH
        self.applied_to = EPOCH
        
    def edit(self, subtypes):
        self._updateProperty('subtypes', subtypes)

    def all_meta_types(self):
        return [
            { 'action' : 'manage_addProduct/BastionLedger/add_asset'
              , 'permission' : OperateBastionLedgers
              , 'name' : 'BLAsset'
              , 'Product' : 'BastionLedger'
              , 'instance' : None
             }
            ]

    def getSubTypes(self):
        """ return a list of legitimate subtype names """
        return self.Ledger.Accounts.uniqueValuesFor('subtype')

    def asset_accounts(self):
        return self.Ledger.Accounts(type='Asset', subtype=self.subtypes)

    def depreciation_methods(self):
        """
        hmmm - these need to be backed up as jurisdiction-related policies calculable from the
        BLAsset data ...
        """
        return getattr(getToolByName(self, 'portal_bastionledger'),
                       'depreciation_tool').depreciation_methods()

    def depreciationAmount(self, date_range, REQUEST=None):
        """
        return the computed depreciation amount for the indicated period
        """
        depreciables = filter(lambda x: x.purchase_date <= max(date_range) and x.totalCost() - x.depreciation_to_date > 0,
                              self.objectValues('BLAsset'))
        if depreciables:
            return reduce(operator.add,
                          map(lambda x,range=saneDateRange(date_range, self.timezone): x.depreciation(range),
                              depreciables))
        return ZCurrency(self.Ledger.defaultCurrency(), 0)

    def manage_applyDepreciation(self, date_range, amount=None,
                                 description='Accumulated Depreciation', force=False, REQUEST=None):
        """
        validate amount against computed and increment asset's depreciation to date
        """
        return self._applyDepreciation(saneDateRange(date_range, self.timezone), amount, description,force,REQUEST)


    def _applyDepreciation(self, date_range, amount=None, description='Accumulated Depreciation',
                           force=False, REQUEST=None):
        txn_id  = ''

        min_dt = floor_date(min(date_range))
        max_dt = ceiling_date(max(date_range))

        depreciation_amount = self.depreciationAmount(date_range)

        if amount and amount != depreciation_amount:
            raise DepreciationError, 'Incorrect Depreciation Amount: %s' % amount

        if (self.applied_from == EPOCH or self.applied_from < min_dt) and \
                (self.applied_to == EPOCH or self.applied_to <= max_dt) or force:

            for asset in self.objectValues('BLAsset'):
                if asset.purchase_date < max(date_range):
                    asset.depreciation_to_date += asset.depreciation(date_range)
                asset.last_depreciation_run = max_dt

        else:
            raise InvalidPeriodError, 'Depreciation already applied within date range (%s,%s)!' % (self.applied_from, self.applied_to)

        if depreciation_amount != 0:
            ledger = self.Ledger
            txn = ledger.createTransaction(title=description,
                                           effective=max(date_range))  # beware to keep this the same as other EOP dates
            manage_addBLEntry(txn, ledger.accountsForTag('dep_exp')[0], depreciation_amount)
            manage_addBLEntry(txn, ledger.accountsForTag('accum_dep')[0], -depreciation_amount)
            txn.manage_post()
            txn_id = txn.getId()

        # note that we've run ...
        self.applied_from = min(self.applied_from, min_dt)
        self.applied_to = max(self.applied_to, max_dt)
        
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Applied Depreciation (%s)' % depreciation_amount)
            return self.manage_depreciation(self, REQUEST)

        return txn_id

    def saneDateRange(self, dates):
        # allow zpt to clean up dates
        return saneDateRange(dates, self.ledger.timezone)
        
    def manage_reset(self, REQUEST=None):
        """
        reset (undepreciate) all assets ...
        """
        for asset in self.objectValues('BLAsset'):
            zero = ZCurrency('%s 0.00' % asset.purchase_price.currency())
            asset._updateProperty('depreciation_to_date', zero)

        self.applied_from = EPOCH
        self.applied_to = EPOCH

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'undepreciated everything')
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLAssetRegister)
    
