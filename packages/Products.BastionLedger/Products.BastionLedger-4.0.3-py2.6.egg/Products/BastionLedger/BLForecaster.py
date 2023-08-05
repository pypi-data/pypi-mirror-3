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
import AccessControl, operator
from DateTime import DateTime
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from BLBase import *
from AccessControl.Permissions import access_contents_information
from Products.CMFCore.permissions import View
from Products.BastionBanking.ZCurrency import ZCurrency
from Permissions import OperateBastionLedgers, ManageBastionLedgers

from zope.interface import Interface, implements
from interfaces.tools import IBLLedgerTool

class IForecast(Interface): pass

def dateFromId(id):
    return DateTime('%s-01' % id)    

def idFromDate(dt):
    return '%s-%0.2i' % (dt.year(), dt.month())

def lastOfMonth(dt):
    """
    the last day of month of related forecast
    """
    if dt.month() == 12:
        return DateTime('%i/12/31' % dt.year())
    else:
        return DateTime('%i/%0.2i/01' % (dt.year(), dt.month() + 1)) - 1

def manage_addBLForecaster(self, id='Forecaster', title='Budgeting tool', REQUEST=None):
    """
    """
    self._setObject(id, BLForecaster(id, title))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_workspace', (REQUEST['URL3'], id))
    return id

class BLForecastRecord(PropertyManager, BSimpleItem):
    """
    A record of the account and gross amount
    """

    meta_type = 'BLForecastRecord'

    _properties = (
        {'id':'amount', 'type':'currency', 'mode':'w'},
        )

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (access_contents_information, ('account',)),
        ) + BSimpleItem.__ac_permissions__

    manage_options = PropertyManager.manage_options + BSimpleItem.manage_options

    def __init__(self, id, amount):
        self.id = id
        self.amount = amount

    def account(self):
        try:
            return self.Ledger._getOb(self.id)
        except:
            return None

    def title(self):
        try:
            return self.account().title
        except:
            return ''

AccessControl.class_init.InitializeClass(BLForecastRecord)

manage_addBLForecastForm = PageTemplateFile('zpt/add_forecast', globals())
def manage_addBLForecast(self, id, title='', REQUEST=None):
    """
    """
    self._setObject(id, BLForecast(id))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_workspace' % REQUEST['URL3'])
    return id

class BLForecast(BObjectManagerTree):
    """
    A group of forecast records for a particular month

    This is an array of BLForecastRecords
    """

    meta_type = 'BLForecast'

    implements(IForecast)
    
    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (access_contents_information, ('firstOfMonth', 'lastOfMonth',)),
        )

    def title(self):
        return self.first_of_month().strftime('%b %Y')

    def firstOfMonth(self):
        """
        the date the forecast is related to (first of month)
        """
        return dateFromId(self.getId())

    def lastOfMonth(self):
        """
        the last day of month of related forecast
        """
        return lastOfMonth(self.firstOfMonth())

AccessControl.class_init.InitializeClass(BLForecast)

class BLForecaster(BObjectManagerTree):
    """
    Capture/display projected versus actuals
    """
    meta_type = portal_type = 'BLForecaster'

    implements(IBLLedgerTool)

    manage_main = PageTemplateFile('zpt/forecast_main', globals())
    manage_btree = BObjectManagerTree.manage_main

    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (access_contents_information, ('accountIds', 'accountValues',)),
        (View, ('forecasts', 'dateRange',)),
        (ManageBastionLedgers, ('edit',)),
        (OperateBastionLedgers, ('manage_editForecasts', 'availableIds', 'makeIds',)),
        )

    _properties = BObjectManagerTree._properties + (
        {'id':'account_ids',  'mode':'w', 'type':'multiple selection', 'select_variable':'accountIds'},
        )

    def __init__(self, id, title, account_ids=[]):
        BObjectManagerTree.__init__(self, id, title)
        self.account_ids = account_ids

    def accountIds(self):
        return self.Ledger.objectIds('BLAccount')

    def accountValues(self):
        return filter(lambda x,ids=self.account_ids: x.getId() in ids,
                      self.Ledger.objectValues('BLAccount'))

    def edit(self, title, description, account_ids):
        self._updateProperty('title', title)
        self._updateProperty('description', description)
        self._updateProperty('account_ids', account_ids)

    def all_meta_types(self):
        return [
            { 'action' : 'manage_addProduct/BastionLedger/add_forecast'
              , 'permission' : OperateBastionLedgers
              , 'name' : 'Forecast'
              , 'Product' : 'BastionLedger'
              , 'instance' : None
             }
            ]

    def makeIds(self, date=None, start_month=-11, end_month=12):
        """ return a list of dates """
        if date is None:
            date = DateTime()
        elif not isinstance(date, DateTime):
            date = DateTime(date)

        month = date.month()
        year = date.year()
        ids = []

        for i in xrange(start_month,end_month):
            if month + i < 1:
                yy = year - 1
                mm = 12 + i + month
            elif month + i > 12:
                yy = year + 1
                mm = i - 12 + month
            else:
                yy = year
                mm = month + i
            ids.append('%s-%0.2i' % (yy, mm))

        return ids

    def availableIds(self, date=DateTime(), start_month=-11, end_month=12):
        """
        return a list if id's representing dates for which we can add forecasts for
        """

        return filter(lambda x,forecasts=self.objectIds(): x not in forecasts,
                      self.makeIds(date, start_month, end_month))

    def dateRange(self):
        return (dateFromId(min(self.objectIds())), dateFromId(max(self.objectIds())))

    def manage_editForecasts(self, recs, REQUEST=None):
        """
        add/edit forecasts - each rec is a hash keyed with 'account', 'amount', and 'date'
        """
        for rec in recs:
            # ignore bullshit/empty amounts
            if not rec['amount']:
                continue
            amount = ZCurrency(rec['amount'])
            id = idFromDate(rec['date'])
            if not getattr(aq_base(self), id, None):
                manage_addBLForecast(self, id)

            forecast = getattr(self, id)
            projection = getattr(forecast, rec['account'], None)
            if not projection:
                forecast._setObject(rec['account'], BLForecastRecord(rec['account'], amount))
            else:
                projection._updateProperty('amount', amount)
                
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def forecasts(self, from_date, number):
        """
        return a list of number (projected, actual) tuples beginning at from_date
        
        the first element is a header with the dates for subsequent elements

        the other elements are (account, budgeted amt, actual amt)

        the final element is a totals summation
        """
        now = DateTime()
        dates = []
        results = []
        recs = {}
        totals = []

        for id in self.makeIds(from_date, 0, number):
            try:
                projection = self._getOb(id)
                effective_date = projection.lastOfMonth()
            except:
                projection = []
                effective_date = lastOfMonth(dateFromId(id))

            for account in self.accountValues():
                if projection:
                    proj_rec = getattr(aq_base(projection), account.getId(), None)
                    if proj_rec:
                        b_amount = proj_rec.amount
                    else:
                        b_amount = ZCurrency(account.base_currency, 0)
                else:
                    b_amount = None

                a_amount = account.balance(effective=effective_date) - \
                    account.balance(effective=lastOfMonth(effective_date - 31))

                if recs.has_key(account):
                    recs[account].extend( [b_amount, a_amount] )
                else:
                    recs[account] = [ b_amount, a_amount ]

            dates.append(effective_date)
            # filtering None's, step through pairs of columns ...
            try:
                b_total = reduce(operator.add,
                                  filter(lambda x: x,
                                         map(lambda x,ndx=2 * len(dates) - 2: x[ndx],
                                             recs.values())))
            except TypeError:
                # attempt to sum an empty list ...
                b_total = ''
            try:
                a_total = reduce(operator.add,
                                  filter(lambda x: x,
                                         map(lambda x,ndx=2 * len(dates) - 1: x[ndx],
                                             recs.values())))
            except TypeError:
                a_total = ''
            totals.extend([b_total, a_total])
            
        # get some dependable sort order ...
        for account in self.accountValues():
            row = []
            row.append(account)
            row.extend(recs[account])
            results.append(row)

        return dates, results, totals

AccessControl.class_init.InitializeClass(BLForecaster)
    
def addForecast(ob, event):
    ledger = ob.Ledger
    # if we're copying, container has no account_ids ...
    for id in getattr(ob.aq_parent, 'account_ids', []):
        ob._setObject(id, BLForecastRecord(id, ledger.zeroAmount()))

