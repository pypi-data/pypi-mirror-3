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
import AccessControl, logging, os, string
from Acquisition import aq_parent, aq_inner, aq_base
from DateTime import DateTime
from AccessControl.Permissions import view_management_screens
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from BLBase import BObjectManager as Folder, ProductsDictionary
from BLGlobals import EPOCH
from utils import ceiling_date, floor_date
from Permissions import ManageBastionLedgers
from BLReport import BLReport
from BLSubsidiaryLedger import BLSubsidiaryLedger
from Exceptions import PostingError

from interfaces.tools import IBLControllerTool

from zope.interface import implements

#
# heh - just generate plain-text reports of our plone-skinned general reports
#
PLAIN_REPORT='''
<html metal:use-macro="context/standard_template.pt/macros/page">
   <div metal:fill-slot="body">
      <div metal:use-macro="context/blreporting_macros/macros/%s-multi"/>
   </div>
</html>
'''


def manage_addPeriodEndTool(self, id='periodend_tool', REQUEST=None):
    """
    """
    self._setObject(id, PeriodEndTool())
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))


class _Entry(dict):
    """
    helper to create transaction(s)
    """
    def __init__(self, amount, account, title=''):
        self.title = title
        self.amount = amount
        self.account = account

class PeriodEndTool(UniqueObject, Folder, ActionProviderBase):
    """
    This tool provides process, control, management, and plugins to run
    end of period processing on BastionLedger's.
    """

    implements(IBLControllerTool)

    id = 'periodend_tool'
    meta_type = 'BLPeriodEndTool'
    portal_type = 'BLTool'

    icon = 'misc_/BastionLedger/blquill'

    __ac_permissions__ = (
        (ManageBastionLedgers, ('manage_periodEnd', 'manage_generateReports',
                                'beforeActionsForLedger',
                                'afterActionsForLedger', 'manage_reset')),
        ) + Folder.__ac_permissions__ + ActionProviderBase.__ac_permissions__

    _properties = Folder._properties + (
        {'id':'periods_to_report',    'type':'int', 'mode':'w'},
        )

    _actions = ()
    periods_to_report = 3

    manage_options = ( 
        Folder.manage_options[0], ) + \
        ActionProviderBase.manage_options + Folder.manage_options[2:]

    def __init__(self, id='', title=''):
        self.title = title

    def all_meta_types(self):
        return []

    def Description(self):
	return self.__doc__

    def manage_periodEnd(self, ledger, effective, force=False):
        """
        do end-of-period closing entries, ledger-specific end-of-period processing
        and bump opening balance entries in all accounts
        """
        REQUEST = self.REQUEST

        if not isinstance(effective, DateTime):
            effective = DateTime(effective)

        effective = floor_date(effective.toZone(ledger.timezone))

        # we need to do the ledger last so that any subsidiary ledger changes are reflected
        # in the control entry
        ledgers = [x for x in filter(lambda x: x.getId() != 'Ledger', ledger.ledgerValues())]
        ledgers.append(ledger.Ledger)

        for led in ledgers:

            id = led.getId()
            tids = []
            start_date = ledger.periods.startForLedger(id, effective)
            end_date = ledger.periods.endForLedger(id, effective)

            assert start_date < end_date, 'Invalid date(s) %s -> (%s, %s)' % (effective, start_date, end_date)
            arguments = dict(REQUEST.get(id, {}))

            # post all auto-correction entries (and tweak reporting lines)
            for func in self.beforeActionsForLedger(led, start_date, end_date):
                tids.extend(func(led, start_date, end_date, force, **arguments))

            # now snapshot balances and reporting amounts 
            pinfo = ledger.periods.addPeriodInfo(led, start_date, end_date, force)

            # roll journals
            tids.extend(self.postClosingEntries(led, start_date, end_date, pinfo, force))

            # do anything else (tweaking balances)
            for func in self.afterActionsForLedger(led, start_date, end_date):
                tids.extend(func(led, start_date, end_date, pinfo, force, **arguments))

            pinfo._updateProperty('transactions', tids)

            # recompute balances to effect closing entries
            pinfo.manage_recompute()

        if not force:
            # ensure everything's kosher (ie no previous period unprocessed entries etc etc)

            # TODO - ensure genuine txns posted in/for the next day don't get picked up ...
            tonight = ceiling_date(end_date)
            for account in ledger.Ledger.accountValues(type=['Income','Expense']):
                # ignore corporation tax posting
                if account.hasTag('tax_exp'):
                    continue
                if account.balance(effective=tonight) != 0:
                    raise PostingError, str(account)

    def manage_generateReports(self, ledger, base_id, effective, 
                               reports=('balance-sheet', 'revenue-statement', 'cashflow-statement'),
                               REQUEST=None):
        """
        create (or recreate) the Balance sheet, P&L, Cashflow statement
        """
        rf = ledger.Reports
        for report in reports:
            template = ZopePageTemplate(report, PLAIN_REPORT % report).__of__(ledger)
            id = '%s-%s' % (report, base_id)
            title = '%s %s' % (string.capwords(report.replace('-', ' ')), effective.strftime('%B %Y'))
            if getattr(aq_base(rf), id, None):
                rf._delObject(id)
            rf._setObject(id, BLReport(id, title, effective, str(template(date=effective))))

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Generated %i reports' % len(reports))
            return self.manage_main(self, REQUEST)

    def postClosingEntries(self, ledger, beginning, effective, pinfo, force):
        """
        create and post a closing transaction for the ledger - and all subsidiary
        journals
        """
        tids = []
        profit = 0
        led = ledger.Ledger

        earnings = led.accountsForTag('retained_earnings')[0]
        entries = []

        #
        # close out all income and expenses ...
        #
        for account in ledger.accountValues(type=['Income', 'Expense']):
            # don't use balance because it relies on us for opening entries - but _sum doesn't compute
            # control entries properly !!!
            #balance = account.total(effective=(beginning, effective))
            balance = account.balance(effective=effective)
            if balance != 0:
                entries.append(_Entry(-balance, account.getId()))


        if entries:
            txn = ledger.createTransaction(title="EOP - Closing Entries",
                                           effective=effective,
                                           entries=entries)
            txn.manage_addProduct['BastionLedger'].manage_addBLEntry(earnings.getId(), -txn.total())
            txn.manage_post()   
            tids.append(txn.getId())

        return tids

    def beforeActionsForLedger(self, ledger, beginning, effective):
        """
        return a list of functors to do end-of-period processing
        """
        if ledger.meta_type in ('BLLedger',):
            return [ self._beforeLedger ]
        if ledger.meta_type in ('BLPayroll', 'FSPayroll'):
            return [ self._beforePayroll ]
        return []

    def afterActionsForLedger(self, ledger, beginning, effective):
        """
        return a list of functors to do end-of-period processing
        """
        if ledger.meta_type in ('BLLedger',):
            return [ self._afterLedger ]
        if ledger.meta_type in ('BLPayroll', 'FSPayroll'):
            return [ self._afterPayroll ]
        return []

    #
    # general file-system end-of-period functions ...
    #
    def _beforePayroll(self, ledger, beginning, effective, force, **kw):
        if kw.get('tax_certs', False):
            ledger.manage_tax_certificates(beginning, effective, send=False)
        # no txns
        return []

    def _afterPayroll(self, ledger, beginning, effective, pinfo, force, **kw):
        # adjust future-dated payment totals
        for employee in ledger.accountValues():
            map(lambda x: x.calculate_running_totals(),
                filter(lambda x, dt=effective: getattr(x.blTransaction(), 'effective_date', EPOCH) >= dt,
                       employee.objectValues('BLPaySlip')))
        # no txns
        return []

    def _beforeLedger(self, ledger, beginning, effective, force, **kw):
        """
        Apply depreciation to general ledger
        """
        tids = []
        bastionledger = ledger.aq_parent

        for assetregister in kw.get('assetregisters', []):
            # only optionally generate txn ... - and don't mangle effective dates
            tid = bastionledger._getOb(assetregister)._applyDepreciation([beginning, effective],
                                                                         description='EOP - Depreciation',
                                                                         force=force)
            if tid:
                tids.append(tid)

        return tids
            
    def _afterLedger(self, ledger, beginning, effective, pinfo, force, **kw):
        """
        General Ledger post-processing - clear our dividends declared, post
        corporation tax, and move current earnings to retained
        """
        tids = []
        bastionledger = ledger.aq_parent
        retained_earnings = ledger.accountsForTag('retained_earnings')[0]
        dividend_ents = []

        #
        # close out all dividend paid accounts
        #
        for account in ledger.accountsForTag('dividend', optional=True):
            balance = account.total(effective=(beginning, effective))
            #balance = account.balance(effective=(beginning, effective))
            if balance != 0:
                dividend_ents.append(_Entry(-balance, account.getId()))

        if dividend_ents:
            txn = ledger.createTransaction(title="EOP - Dividend cleardown",
                                           effective=effective,
                                           entries=dividend_ents)
            txn.manage_addProduct['BastionLedger'].manage_addBLEntry(retained_earnings.getId(), 
                                                                     -txn.total())
            txn.manage_post()
            tids.append(txn.getId())

        self.manage_generateReports(bastionledger, 
                                    pinfo.aq_parent.getId(), 
                                    effective, kw.get('reports',[]))

        # calculate corporation tax
        tax = pinfo.company_tax
        if tax != 0:

            tax_exp = ledger.accountsForTag('tax_exp')[0]
            acc_tax = ledger.accountsForTag('tax_accr')[0]

            tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(title="EOP - Corporation Tax",
                                                                                    effective=effective)
            txn = ledger._getOb(tid)
            txn.manage_addProduct['BastionLedger'].manage_addBLEntry(tax_exp.getId(), tax)
            txn.manage_addProduct['BastionLedger'].manage_addBLEntry(acc_tax.getId(), -tax)
            txn.manage_post()

            tids.append(tid)
            
            pinfo._getOb(acc_tax.getId()).reporting_balance -= tax

        current_earnings = ledger.accountsForTag('profit_loss')[0]
  
        # move periods current earnings (and profit) to retained earnings
        current = current_earnings.balance(effective=effective)

        if current != 0 and current_earnings != retained_earnings:
            # post this in new period so it rolls into next periods period end ...
            tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(title="EOP - Current to retained",
                                                                                    effective=effective)
            retained_txn = ledger._getOb(tid)
            retained_txn.manage_addProduct['BastionLedger'].manage_addBLEntry(current_earnings.getId(), -current)
            retained_txn.manage_addProduct['BastionLedger'].manage_addBLEntry(retained_earnings.getId(), current)
                
            retained_txn.manage_post()
            tids.append(tid)

        return tids

    def manage_reset(self, ledger, REQUEST=None):
        """
        roll back the entire thing and start again ...
        """
        # roll back all the txns
        ledger.periods.manage_delObjects(list(ledger.periods.objectIds('BLPeriodInfos')))

        # unset all depreciations
        for reg in ledger.objectValues('BLAssetRegister'):
            reg.manage_reset()

        # remove all standard reports
        rmids = []
        for reportid in ledger.Reports.objectIds():
            for stdrpt in ('balance-sheet', 'revenue-statement', 'cashflow-statement'):
                if reportid.startswith(stdrpt):
                    rmids.append(reportid)
        if rmids:
            ledger.Reports.manage_delObjects(rmids)

AccessControl.class_init.InitializeClass(PeriodEndTool)


