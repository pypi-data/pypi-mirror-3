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
import AccessControl
from DateTime import DateTime
from Acquisition import Implicit, aq_base
from AccessControl.Permissions import access_contents_information, view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import getToolByName
from BLBase import BObjectManagerTree as Folder
from BLBase import PortalContent as SimpleItem
from BLGlobals import EPOCH
from Exceptions import InvalidPeriodError
from Permissions import ManageBastionLedgers
from utils import floor_date, ceiling_date, month_ending_date

class BLPeriodRec(SimpleItem):
    """
    Stores balances for period-ends, and separately, reporting amounts.  These balances
    are used elsewhere to quickly compute account totals.  The reporting amounts are
    independent of this, and used to collate prior-period reports.
    """
    meta_type = 'BLPeriodRec'

    icon = 'misc_/BastionLedger/blaccount'

    Types = ('Asset', 'Liability', 'Proprietorship', 'Income', 'Expense')

    _properties = (
        {'id':'accno',             'type':'string',      'mode':'w'},
        {'id':'title',             'type':'string',      'mode':'w'},
        {'id':'type',              'type':'selection',   'mode':'w', 'select_variable':'Types'},
        {'id':'balance',           'type':'currency',    'mode':'w'},
        {'id':'reporting_balance', 'type':'currency',    'mode':'w'},
        )

    def __init__(self, id, title, accno, type, balance):
        self.id = id
        self.accno = accno
        self.title = title
        self.type = type
        self.balance = balance            # cached for opening balance enquiries
        self.reporting_balance = balance  # used in financial reports - might be tweaked ...

    def effective(self):
        """ the effective date of the *cached* entry """
        return self.aq_parent.period_ended

AccessControl.class_init.InitializeClass(BLPeriodRec)
    

class BLPeriodInfo(Folder):
    """
    statistics info for ledger for a reporting period
    """
    meta_type = portal_type = 'BLPeriodInfo'

    icon = 'misc_/BastionLedger/blledger'

    manage_main = PageTemplateFile('zpt/period_chart', globals())
    manage_transactions = PageTemplateFile('zpt/period_txns', globals())

    manage_options = (
        {'label':'Accounts',     'action':'manage_main'},
        {'label':'Transactions', 'action':'manage_transactions'},
        {'label':'Properties',   'action':'manage_propertiesForm'},
        {'label':'Recalculate',  'action':'manage_recompute'},
        ) + Folder.manage_options[1:]

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view_management_screens, ('manage_transactions',)),
        (ManageBastionLedgers, ('bumpReportingAmount',)),
        (access_contents_information, ('blLedger', 'blLedgerTransactions', 'account','balance', 
                                       'getAccountInfos', 'prevPeriodInfo',
                                       'nextPeriodInfo')),
        )
    
    _properties = (
       {'id':'num_accounts',     'type':'int',      'mode':'w'},
       {'id':'num_transactions', 'type':'int',      'mode':'w'},
       {'id':'period_began',     'type':'date',     'mode':'w'},
       {'id':'period_ended',     'type':'date',     'mode':'w'},
       {'id':'gross_profit',     'type':'currency', 'mode':'w'},
       {'id':'net_profit',       'type':'currency', 'mode':'w'},
       {'id':'company_tax',      'type':'currency', 'mode':'w'},
       {'id':'losses_forward',   'type':'currency', 'mode':'w'},
       {'id':'transactions',     'type':'lines',    'mode':'w'},
       )

    def __init__(self, id, period_began, period_ended, num_accounts, num_transactions, 
                 gross_profit, net_profit, company_tax, losses_forward):
        Folder.__init__(self, id)
        self.period_began = period_began
        self.period_ended = period_ended
        self.num_accounts = num_accounts
        self.num_transactions = num_transactions
        self.gross_profit = gross_profit
        self.net_profit = net_profit
        self.company_tax = company_tax
        self.losses_forward = losses_forward
        self.transactions = []

    def blLedger(self):
        """
        returns the underlying ledger (or None if it's no longer present)
        """
        try:
            return self.bastionLedger()._getOb(self.getId())
        except:
            pass
        return None

    def blLedgerTransactions(self):
        """
        the individual transactions incorporated within this period
        """
        ledger = self.blLedger()
        if ledger:
            return ledger.transactionValues(effective_date={'query': (self.period_began,
                                                                      self.period_ended),
                                                            'range':'minmax'},
                                            sort_on='effective_date',
                                            sort_order='descending')
        return []

    def balance(self, accountid):
        """
        return our cached balance for the account
        """
        try:
            return self._getOb(accountid).balance
        except:
            pass
        return self.zeroAmount()

    def account(self, accountid):
        """
        return the ledger account (if found)
        """
        try:
            return self.blLedger()._getOb(accountid)
        except:
            pass
        return None

    def bumpReportingAmount(self, accountid, amount):
        """
        tweaking a reporting entry
        """
        acc = self._getOb(accountid)
        rpt_bal = self._getOb(accountid).reporting_balance
        acc._updateProperty('reporting_balance', rpt_bal + amount)

    def manage_updateReportingBalances(self, balances, REQUEST=None):
        """ 
        balances is a list of id,amount records of accountid/new balance's ...
        """
        for rec in balances:
            self._getOb(rec['id'])._updateProperty('reporting_balance', rec['amount'])

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Updated reporting balances')
            return self.manage_main(self, REQUEST)

    def getAccountInfos(self):
        """
        collate and return account information
        """
        infos = []
        my_url = self.absolute_url()
        prev_info = self.prevPeriodInfo()

        for rec in self.objectValues():

            if prev_info:
                opening = prev_info.balance(rec.getId())
            else:
                opening = self.zeroAmount()

            try:
                account = self.account(rec.getId())
                infos.append({'id':rec.getId(),
                              'absolute_url':account.absolute_url(),
                              'real_url':'%s/%s' % (my_url, rec.getId()),
                              'icon':account.getIcon(1),
                              'accno':rec.accno,
                              'type': rec.type,
                              'title':rec.title,
                              'opening': opening,
                              'change': opening - rec.balance,
                              'balance':rec.balance,
                              'reporting_balance':rec.reporting_balance})
            except:
                infos.append({'id':rec.getId(),
                              'absolute_url':my_url,
                              'real_url':'%s/%s' % (my_url, rec.getId()),
                              'icon': 'broken.gif',
                              'type':rec.type,
                              'accno': rec.accno,
                              'title': rec.title,
                              'opening': opening,
                              'change': opening - rec.balance,
                              'balance':rec.balance,
                              'reporting_balance':rec.reporting_balance})
        #infos.sort(lambda x,y: x['accno'] < y['accno'])
        return infos

    def blTransactions(self):
        """
        return all the transactions associated with (ie generated by) this period end
        """
        results = []
        ledger = self.blLedger()
        for tid in self.transactions:
            try:
                results.append(ledger._getOb(tid))
            except:
                pass
        return  results

    def manage_recompute(self, REQUEST=None, **kw):
        """
        recalculate the balances
        """
        ledger = self.blLedger()

        began = self.period_began
        ended = self.period_ended

        for account in ledger.accountValues():
            rec = getattr(aq_base(self), account.getId(), None)
            if rec:
                # we need to take into account control entries and 'strange' summations ...
                # TODO - optimise this !!
                amount = account.openingBalance(began) + account.total(effective=(began, ended))
                rec._updateProperty('balance', amount)
        
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def __cmp__(self, other):
        """
        return a sorted list of these
        """
        if not isinstance(other, BLPeriodInfo): return -1
        
        for attr in ('id', 'period_ended'):
            mine = getattr(self, attr)
            theirs = getattr(other, attr)

            if mine > theirs: return 1
            if mine < theirs: return -1

        return 0

    def manage_beforeDelete(self, item, container):
        """
        roll back period end effects
        """
        if self.transactions:
            self.blLedger().manage_delObjects(self.transactions)

    def prevPeriodInfo(self):
        """
        return the period info for the period prior to this
        """
        try:
            return self.aq_parent.aq_parent.periodForLedger(self.getId(),
                                                            self.period_began - 1)
        except ValueError:
            pass
        return None

    def nextPeriodInfo(self):
        """
        return the period info for the period after this
        """
        try:
            info = self.aq_parent.aq_parent.periodForLedger(self.getId(),
                                                            self.period_ended + 1)
        except ValueError:
            return None
        
        # just make sure it's not fallen back to ourselves ..
        if info == self:
            return None

        return info

AccessControl.class_init.InitializeClass(BLPeriodInfo)


class BLPeriodInfos(Folder):
    """
    a container of PeriodInfo's for a ledger - the id is the same as the
    ledger it maps
    """
    meta_type = portal_type = 'BLPeriodInfos'

    icon = 'misc_/BastionLedger/period'

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view_management_screens, ('manage_transactions',)),
        (access_contents_information, ('blTransactions', 'transactionValues', 'effective')),
        )

    manage_transactions = PageTemplateFile('zpt/period_txns', globals())

    manage_options = (
        Folder.manage_options[0],
        {'label':'View',         'action':''},
        {'label':'Properties',   'action':'manage_propertiesForm'},
        {'label':'Transactions', 'action':'manage_transactions'},
        ) + Folder.manage_options[1:]

    def Title(self):
        """
        """
        yy,mm,dd = self.getId().split('-')
        # hmmm DateTime screws up timezones ...
        return '%s %s' % (dd, DateTime(self.getId()).strftime('%B %Y'))

    def blTransactions(self):
        """
        return list of closing transactions across all ledgers
        """
        txns = []
        for ledger in self.objectValues():
            txns.extend(ledger.blTransactions())

        return txns
        
    # transaction API ...
    def transactionValues(self, REQUEST={}, **kw):
        """
        the list of period-end generated transactions
        """
        # ignore filter
        return self.blTransactions()

    def effective(self):
        """
        the effective date for the period-end record
        """
        return floor_date(DateTime('%s %s' % (self.getId(), self.timezone)))

AccessControl.class_init.InitializeClass(BLPeriodInfos)


class BLLedgerPeriodsFolder(Folder):
    """
    a container of LedgerPeriod's for a set of ledger's
    """

    id = 'periods'
    meta_type = 'BLLedgerPeriodsFolder'

    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view_management_screens, ('manage_balanceSheet', 'manage_revenueStatement', 'manage_trialBalance')),
        (access_contents_information, ('periodsForLedger', 'lastPeriodForLedger', 'infosForDate',
                                       'lastClosingForLedger', 'balanceForAccount',
                                       'startForLedger', 'endForLedger', 'periodEnds', 'nextPeriodEnd',
                                       'ledgerInfos',)),
        (ManageBastionLedgers, ('addPeriodInfo',)),
        )

    default_page = 'blledger_listing'

    manage_runend = PageTemplateFile('zpt/period_runend', globals())
    manage_balanceSheet = PageTemplateFile('zpt/balance_sheet_multi', globals())
    manage_revenueStatement = PageTemplateFile('zpt/revenue_statement_multi', globals())
    manage_trialBalance = PageTemplateFile('zpt/periods_trialbalance', globals())
    manage_ledgers = PageTemplateFile('zpt/periods_ledgers', globals())

    manage_options = (
        {'label':'Periods', 'action':'manage_main'},
        {'label':'Run',  'action':'manage_runend'},
        {'label':'Ledgers', 'action':'manage_ledgers'},
        {'label':'BSheet', 'action':'manage_balanceSheet'},
        {'label':'P & L',  'action':'manage_revenueStatement'},
        {'label':'Balances',  'action':'manage_trialBalance'},
        ) + Folder.manage_options[2:]

    def __init__(self):
        Folder.__init__(self, self.id)

    def infosForDate(self, effective):
        """
        return the period information for the effective date (or None)
        """
        for infos in self.objectValues('BLPeriodInfos'):
            if effective <= infos.effective():
                return infos

        return None

    def periodsForLedger(self, ledgerid):
        """
        returns the folder of BLPeriodInfo objects for the indicated ledger id
        """
        periods = []
        for info in self.objectValues('BLPeriodInfos'):
            try:
                periods.append(info._getOb(ledgerid))
            except KeyError:
                pass

        # we're invariably going to do date-based ranking ...
        periods.sort()
        return periods
    
    def lastPeriodForLedger(self, ledgerid):
        """
        returns the latest BLPeriodInfo for the indicated ledger id
        """
        try:
            return max(self.periodsForLedger(ledgerid))
        except:
            return None

    def lastClosingForLedger(self, ledgerid, effective=None):
        """
        returns the period end date for the latest BLPeriodInfo of the indicated
        ledger

        effective date is for (forced) reruns etc
        """
        if effective:
            periods = self.periodsForLedger(ledgerid)
            periods.reverse()
            eff_max = ceiling_date(effective)
            for period in periods:
                # if it's the end date ...
                if eff_max >= period.period_ended:
                    return period.period_ended
                #if period.period_began == EPOCH:
                #    return EPOCH
                #if eff_max >= period.period_began:
                #    return period.period_ended
            return EPOCH

        try:
            return self.lastPeriodForLedger(ledgerid).period_ended
        except:
            pass

        return EPOCH

    def periodForLedger(self, ledgerid, effective):
        """
        return the period record for the ledger, immediately prior to effective
        """
        periods = self.periodsForLedger(ledgerid)
        periods.reverse()

        for period in periods:
            # if it's a prior period, or on the same end day (dunno why this is two...)
            if effective >= period.period_ended or period.period_ended - effective <= 1.0:
                return period
        raise ValueError, '%s: No period found' % ledgerid

    def startForLedger(self, ledgerid, effective):
        """
        return the start date for the indicated period (possibly that of an earlier run)
        """
        periods = self.periodsForLedger(ledgerid)
        periods.reverse()
        for period in periods:
            if effective >= period.period_began and effective <= period.period_ended:
                return period.period_began
        try:
            dt = self.lastClosingForLedger(ledgerid, effective)
            if dt != EPOCH:
                return floor_date(dt + 1)
        except:
            pass

        return EPOCH

    def endForLedger(self, ledgerid, effective):
        """
        return the end date for the indicated period (possibly that of an earlier run)
        """
        periods = self.periodsForLedger(ledgerid)
        periods.reverse()
        for period in periods:
            if effective >= period.period_began and effective <= period.period_ended:
                return period.period_ended

        return effective

    def balanceForAccount(self, effective, ledgerid, accountid):
        """
        returns the closing balance for the indicated in the indicated ledger
        for the BLPeriodInfo in which the effective date falls
        """
        try:
            return self._balanceForAccount(effective, ledgerid, accountid)
        except (ValueError, TypeError, KeyError):
            # no period end run yet ...
            pass
        return self.zeroAmount()

    def _balanceForAccount(self, effective, ledgerid, accountid):
        """
        returns the closing balance for the indicated in the indicated ledger
        for the BLPeriodInfo in which the effective date falls
        """
        info = self.periodForLedger(ledgerid, effective)
        return info.balance(accountid)


    def addPeriodInfo(self, ledger, period_began, period_ended, force=False):
        """
        """
        # hmmm - start/end is a bit dubious ...
        if period_began >= period_ended - 30:
            raise InvalidPeriodError, 'began greater than ended (give or take a month) %s > %s!' % (period_began, period_ended)

        # hmmm - we've got shite tz issues around this ...
        infosid = month_ending_date(period_ended).strftime('%Y-%m-%d')
        ledgerid = ledger.getId()

        try:
            infos = self._getOb(infosid)
        except:
            self._setObject(infosid, BLPeriodInfos(infosid))
            infos = self._getOb(infosid)

        last_infos = self.periodsForLedger(ledgerid)
        if last_infos:
            last = max(last_infos)
            if period_began < last.period_ended and not force:
                raise InvalidPeriodError, 'date overlap!'
        
        # remove the results of any previous run ...
        if getattr(aq_base(infos), ledgerid, None):
            infos._delOb(ledgerid)

        effective = (period_began, period_ended)

        if ledgerid == 'Ledger':
            theledger = ledger.aq_parent

            # TODO - this doesn't seem to quite add to R - E !!
            gross = theledger.gross_profit(effective)

            try:
                losses = self.periodForLedger('Ledger', period_began - 1).losses_forward
            except:
                losses = self.zeroAmount()

            if gross > 0:
                attributable = min(losses, gross)
            else:
                attributable = self.zeroAmount()

            tax = theledger.corporation_tax(effective, 
                                            gross_profit=gross, 
                                            attributable_losses=attributable)

            net = theledger.net_profit(effective, 
                                       gross_profit=gross, 
                                       corporation_tax=tax, 
                                       attributable_losses=attributable)
            
            # actual losses forward need to be computed
            if net < 0:
                losses = abs(losses - attributable) - net
            else:
                losses = abs(losses - attributable)
        else:
            gross = net = tax = losses = ledger.zeroAmount()

        # we need to compute balances *before* writing new info and screwing with
        # opening balance computations
        recs = map(lambda a: BLPeriodRec(a.getId(), a.title, a.accno, a.type, 
                                         a.balance(effective=period_ended, 
                                                   currency=ledger.defaultCurrency())),
                   ledger.accountValues())

        infos._setObject(ledgerid,
                         BLPeriodInfo(ledgerid,
                                      period_began,
                                      period_ended,
                                      len(ledger.Accounts.searchResults(CreationDate={'query':(EPOCH, period_ended), 'range':'minmax'})),
                                      len(ledger.Transactions.searchResults(effective_date={'query':effective, 'range':'minmax'})),
                                      gross,
                                      net,
                                      tax,
                                      losses))

        pi = infos._getOb(ledgerid)
        for a in recs:
            pi._setObject(a.getId(),a)

        return pi

    def infoForType(self, account_type, numperiods):
        """
        return a dict of stuff from Ledger periods for multi-period reporting
        """
        accno_id = {}
        id_title = {}
        id_balances = {}
        totals = []
        dates = []
        stats = []

        periods = list(filter(lambda x: getattr(aq_base(x), 'Ledger', None),
                              self.objectValues('BLPeriodInfos')))
        periods.reverse()
        periods = periods[:numperiods]

        ndx = 0

        # parse and collate the Ledger info's
        for period in map(lambda x: getattr(x, 'Ledger'), periods):

            zero = period.zeroAmount()
            total = zero

            for rec in filter(lambda x: x.type == account_type, period.objectValues()):

                key = rec.getId()
                
                if accno_id.has_key(rec.accno) and accno_id[rec.accno] != key:
                    raise AssertionError, 'You have an inconsistent accno (%s)!!' % rec.accno

                accno_id[rec.accno] = key

                if not id_title.has_key(key):
                    id_title[key] = rec.title
                
                if not id_balances.has_key(key):
                    balances = [zero for i in periods]
                    id_balances[key] = balances

                id_balances[key][ndx] = rec.reporting_balance
                
                total = rec.reporting_balance + total

            # look behind to get the losses
            try:
                losses = self.periodForLedger('Ledger', period.period_began - 1).losses_forward
            except:
                losses = self.zeroAmount()

            if losses > 0 and period.gross_profit > 0:
                attributable = min(period.gross_profit, losses)
            else:
                attributable = self.zeroAmount()

            totals.append(total)
            dates.append(period.period_ended)
            stats.append({'gross_profit':period.gross_profit,
                          'net_profit':period.net_profit,
                          'company_tax':period.company_tax,
                          'losses_attributable':attributable,
                          'losses_forward':losses})
            ndx += 1

        results = []
        
        sort_order = accno_id.keys()
        sort_order.sort()

        for key in map(lambda x: accno_id[x], sort_order):
            rec = [id_title[key]]
            rec.extend(id_balances[key])
            results.append(rec) 

        return {'accounts':results,      # ordered list
                'balances': id_balances, # keyed on accountids
                'totals':totals,         # list of summations
                'dates':dates,           # list of dates for which the above relates
                'stats':stats}           # gross, net, tax

    def periodEnds(self):
        """
        a list of end dates for which periods have been run
        """
        return map(lambda x: x.Ledger.period_ended, 
                   filter(lambda x: getattr(aq_base(x), 'Ledger', None),
                          self.objectValues('BLPeriodInfos')))

    def periodIds(self):
        """
        return a list of ids for the period records we have
        """
        return self.objectIds('BLPeriodInfos')

    def getAccountInfos(self, periodid=''):
        """
        get a complete set of infos across all journals for a period
        """
        if not periodid:
            infos = self.objectValues('BLPeriodInfos')[0]
        else:
            infos = self._getOb(periodid)

        results = []
        for ledger in infos.objectValues('BLPeriodInfo'):
            results.extend(ledger.getAccountInfos())

        return results

    def nextPeriodEnd(self):
        """
        return the date for the next period end - or a guess at least ...
        """
        # first try and compute day from existing intra-period runs
        ends = self.periodEnds()
        if len(ends) >= 2:
            last = ends[-1]
            return last + (last - ends[-2])

        # grab it from the ledger tool
        lt = getToolByName(self, 'portal_bastionledger', None)
        if lt:
            return lt.yearEnd()
        
        # oh well - return today ...
        return DateTime()

    def manage_reset(self, REQUEST=None):
        """
        hmmm - reset periods if it's in a funk
        """
        Folder.__init__(self, self.id)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reinitialized periods')
            return self.manage_main(self, REQUEST)

    def ledgerInfos(self, REQUEST=None):
        """
        a list of ledger period-ended information
        """
        results = {}
        for period in self.objectValues('BLPeriodInfos'):
            for ledger in period.objectValues('BLPeriodInfo'):
                id = ledger.getId()
                if results.has_key(id):
                    results[id]['periods'][period.getId()] = period
                else:
                    results[id] = {'ledger': id,
                                   'periods': { period.getId(): period },}

        return tuple(results.values())

AccessControl.class_init.InitializeClass(BLLedgerPeriodsFolder)


# deprecated
class BLLedgerPeriods(Folder): pass
