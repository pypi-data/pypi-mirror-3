#
#    Copyright (C) 2008-2009  Corporation of Balclutha. All rights Reserved.
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

from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase  # this fixes up PYTHONPATH :)
from Products.BastionLedger.tests import LedgerTestCase

from Products.BastionLedger.Exceptions import InvalidPeriodError
from Products.BastionLedger.utils import ceiling_date, floor_date
from Products.BastionLedger.BLGlobals import EPOCH

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency

class TestPeriodEnd(LedgerTestCase.LedgerTestCase):

    def testCreated(self):
        self.failUnless(self.controller_tool.periodend_tool)
	

    def testStartForLedger(self):
        effective = DateTime('2009/01/01')
        periods = self.portal.ledger.periods

        self.assertEqual(periods.lastClosingForLedger('Ledger'), EPOCH)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective), EPOCH)
        self.assertEqual(periods.startForLedger('Ledger', effective), EPOCH)

        periods.addPeriodInfo(self.ledger.Ledger, EPOCH, effective)

        self.assertEqual(periods.startForLedger('Ledger', effective), EPOCH)
        self.assertEqual(periods.lastClosingForLedger('Ledger'), effective)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective), effective)

        self.assertEqual(periods.startForLedger('Ledger', effective+2), effective+1)
        self.assertEqual(periods.lastClosingForLedger('Ledger', effective+2), effective)


    def testRunReRun(self):
        now = DateTime(self.ledger.timezone)
        pe_tool = self.controller_tool.periodend_tool

        pe_tool.manage_periodEnd(self.ledger, now+1)

        self.assertRaises(InvalidPeriodError, pe_tool.manage_periodEnd, self.ledger, now+1)

        pe_tool.manage_periodEnd(self.ledger, now+1, force=True)
        #self.assertEqual(len(self.ledger.transactionValues(title='EOP', case_sensitive=True)), 4)

        pe_tool.manage_reset(self.ledger)
        #self.assertEqual(len(self.ledger.transactionValues(title='EOP', case_sensitive=True)), 0)

    def testLossClosingEntries(self):
        ledger = self.portal.ledger
        Ledger = ledger.Ledger
        p1_dt = DateTime('2009/06/30')

        # hmmm - a couple of expense txns ...
        tid = Ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(title='My Txn', effective=p1_dt-20)
	txn = Ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', '-GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000042', ZCurrency('GBP 10.00'))
        txn.manage_post()

        self.assertEqual(Ledger.A000001.balance(effective=p1_dt), ZCurrency('-GBP 10.00'))
        self.assertEqual(Ledger.A000042.balance(effective=p1_dt), ZCurrency('GBP 10.00'))
        self.assertEqual(Ledger.A000042.type, 'Expense') # need something to close out (insurance exp)


        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt), EPOCH)

        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p1_dt)

        pinfo = ledger.periods.objectValues()[0].Ledger

        self.assertEqual(pinfo.num_accounts, 0)  # eek 
        self.assertEqual(pinfo.num_transactions, 1)
        self.assertEqual(pinfo.period_began, EPOCH)
        self.assertEqual(pinfo.period_ended, ceiling_date(p1_dt))
        self.assertEqual(pinfo.gross_profit, ZCurrency('-GBP 10.00'))
        self.assertEqual(pinfo.net_profit, ZCurrency('-GBP 10.00'))
        self.assertEqual(pinfo.company_tax, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfo.losses_forward, ZCurrency('GBP 10.00'))

        self.assertEqual(pinfo.balance('A000001'), ZCurrency('-GBP 10.00'))
        self.assertEqual(pinfo.balance('A000042'), ZCurrency('GBP 0.00'))

        self.assertEqual(ledger.periods.periodForLedger('Ledger', p1_dt + 1), pinfo)
        self.assertEqual(ledger.periods.periodForLedger('Ledger', p1_dt), pinfo)
        self.assertRaises(ValueError, ledger.periods.periodForLedger, 'Ledger', p1_dt - 1)
        self.assertRaises(ValueError, ledger.periods.periodForLedger, 'Ledger', p1_dt - 10)

        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt - 1), EPOCH)
        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt), ceiling_date(p1_dt))
        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt + 1), ceiling_date(p1_dt))


        self.assertEqual(ledger.periods.balanceForAccount(p1_dt + 1, 'Ledger', 'A000001'), ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt, 'Ledger', 'A000001'), ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt - 1, 'Ledger', 'A000001'), ZCurrency('GBP 0.00')) # prev period
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt + 1, 'Ledger', 'A000042'), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt, 'Ledger', 'A000042'), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt - 1, 'Ledger', 'A000042'), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p1_dt - 10, 'Ledger', 'A000042'), ZCurrency('GBP 0.00'))

        # checked newly cached amounts still compute correct balances for A, L, P's ...
        account = Ledger.A000001
        self.assertEqual(account.openingBalance(effective=p1_dt + 1), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.openingBalance(effective=p1_dt), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.openingBalance(effective=p1_dt - 1), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.openingBalance(effective=p1_dt - 10), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.openingBalance(effective=p1_dt - 30), ZCurrency('GBP 0.00'))

        self.assertEqual(account.openingDate(effective=p1_dt + 1), p1_dt + 1)
        self.assertEqual(account.openingDate(effective=p1_dt), p1_dt + 1)
        self.assertEqual(account.openingDate(effective=p1_dt - 1), EPOCH)
        self.assertEqual(account.openingDate(effective=p1_dt - 10), EPOCH)
        self.assertEqual(account.openingDate(effective=p1_dt - 30), EPOCH)

        self.assertEqual(account.total(effective=(p1_dt - 10,p1_dt)), ZCurrency('GBP 0.00'))
        self.assertEqual(account.total(effective=(p1_dt - 30,p1_dt)), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.total(effective=(p1_dt - 1, p1_dt)), ZCurrency('GBP 0.00'))

        self.assertEqual(account.balance(effective=p1_dt + 1), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.balance(effective=p1_dt), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.balance(effective=p1_dt - 1), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.balance(effective=p1_dt - 10), ZCurrency('-GBP 10.00'))
        self.assertEqual(account.balance(effective=p1_dt - 30), ZCurrency('GBP 0.00'))

        self.assertEqual(Ledger.sum(tags='retained_earnings', effective=p1_dt+1), ZCurrency('GBP 10.00'))

        self.assertEqual(len(pinfo.blTransactions()), 1) # closing

        closing = pinfo.blTransactions()[0]

        self.assertEqual(closing.effective_date, floor_date(p1_dt))
        self.assertEqual(closing.debitTotal(), ZCurrency('GBP 10.00'))

        self.assertEqual(ledger.losses_attributable(p1_dt+1, ZCurrency('GBP 50.00')), ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.losses_attributable(p1_dt+1, ZCurrency('GBP 5.00')), ZCurrency('GBP 5.00'))

        return

        # this is pre-closing entry
        self.assertEqual(ledger.A000042.openingBalance(p1_dt+2), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.A000042.balance(effective=p1_dt+2), ZCurrency('GBP 0.00'))

        xfer = pinfo.blTransactions()[1]
        self.assertEqual(xfer.effective_date, floor_date(p1_dt+2)) # must be into next period

    def testProfitClosingEntries(self):
        # tests profit + subsidiary ledger balances which have proved problematic

        order_dt = DateTime('2007/06/20')
        p1_dt = DateTime('2007/06/30')
        p2_dt = DateTime('2008/06/30')
        p3_dt = DateTime('2009/06/30')

        self.ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart('widget')
        self.widget = self.ledger.Inventory.widget

        ledger = self.ledger.Ledger

        income = ledger.accountsForTag('part_inc')[0]
        self.widget.edit_prices('kilo', 1.5, 5,
                                ZCurrency('GBP20'),
                                ZCurrency('GBP10'),
                                ZCurrency('GBP10'),
                                ledger.accountsForTag('part_inv')[0].getId(),
                                income.getId(),
                                ledger.accountsForTag('part_cogs')[0].getId())

        receivables = self.ledger.Receivables
        control = receivables.controlAccount()

        receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = receivables.A1000000

        account.manage_addOrder(orderdate=order_dt)
        order = account.objectValues('BLOrder')[0]
        order.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        order.manage_invoice()

        # wtf is the txn??
        self.assertEqual(order.status(), 'invoiced')
        otxn = order.blTransaction()
        self.assertEqual(otxn.status(), 'posted')
        self.assertEqual(otxn.effective_date, order_dt)

        self.assertEqual(account.balance(effective=order_dt + 1), ZCurrency('GBP 22.00'))
        self.assertEqual(account.balance(effective=order_dt), ZCurrency('GBP 22.00'))
        self.assertEqual(control.balance(effective=order_dt + 1), ZCurrency('GBP 22.00'))
        self.assertEqual(control.balance(effective=order_dt), ZCurrency('GBP 22.00'))
        self.assertEqual(income.balance(effective=order_dt), ZCurrency('-GBP 20.00'))

        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p1_dt)

        pinfoid = p1_dt.strftime('%Y-%m-%d')
        pinfoR = ledger.periods._getOb(pinfoid).Receivables
        pinfoL = ledger.periods._getOb(pinfoid).Ledger

        self.assertEqual(ledger.periods.periodForLedger('Receivables', p1_dt+2), pinfoR)
        self.assertRaises(ValueError, ledger.periods.periodForLedger, 'Ledger', p1_dt - 1)

        self.assertEqual(pinfoR.num_accounts, 0)     # eek
        self.assertEqual(pinfoR.num_transactions, 1)
        self.assertEqual(pinfoR.period_began, EPOCH)
        self.assertEqual(pinfoR.period_ended, ceiling_date(p1_dt))

        self.assertEqual(list(pinfoR.objectIds()), [account.getId()]) 

        self.assertEqual(pinfoL.gross_profit, ZCurrency('GBP 10.00'))
        self.assertEqual(pinfoL.net_profit, ZCurrency('GBP 7.00'))
        self.assertEqual(pinfoL.company_tax, ZCurrency('GBP 3.00'))
        self.assertEqual(pinfoL.losses_forward, ZCurrency('GBP 0.00'))

        self.assertEqual(pinfoR.balance(account.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(pinfoL.balance(income.getId()), ZCurrency('GBP 0.00')) # it's had closing applied
        self.assertEqual(pinfoL.balance(control.getId()), ZCurrency('GBP 22.00')) # it's had closing applied
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Ledger', income.getId()), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Ledger', control.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Receivables', account.getId()), ZCurrency('GBP 22.00'))

        self.assertEqual(ledger.sum(tags='retained_earnings', effective=p1_dt+2), ZCurrency('-GBP 10.00'))

        self.assertEqual(len(pinfoL.blTransactions()), 2) # closing + tax
        self.assertEqual(len(pinfoR.blTransactions()), 0) # no I or E a/c's

        closing = pinfoL.blTransactions()[0]

        self.assertEqual(closing.effective_date, p1_dt)
        self.assertEqual(closing.debitTotal(), ZCurrency('GBP 20.00'))

        self.assertEqual(ledger.losses_attributable(p2_dt, ZCurrency('GBP 50.00')), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.losses_attributable(p2_dt, ZCurrency('GBP 5.00')), ZCurrency('GBP 0.00'))

        tax = pinfoL.blTransactions()[1]

        self.assertEqual(tax.effective_date, p1_dt)
        self.assertEqual(tax.debitTotal(), ZCurrency('GBP 3.00'))

        # run another period end and see if the receivables balance carries over
        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p2_dt)

        pinfoid = p2_dt.strftime('%Y-%m-%d')
        pinfoR = ledger.periods._getOb(pinfoid).Receivables
        pinfoL = ledger.periods._getOb(pinfoid).Ledger

        self.assertEqual(pinfoR.num_transactions, 0) # no new txns

        self.assertEqual(pinfoL.gross_profit, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.net_profit, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.company_tax, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.losses_forward, ZCurrency('GBP 0.00'))

        self.assertEqual(pinfoR.balance(account.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(pinfoL.balance(income.getId()), ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.balance(control.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Ledger', control.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Receivables', account.getId()), ZCurrency('GBP 22.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p2_dt, 'Ledger', income.getId()), ZCurrency('GBP 0.00'))


        # now pay the bill ...
        txn = self.ledger.Receivables.createTransaction(effective=p3_dt-10)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', ZCurrency('GBP 22.00'))
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(account.getId(),-ZCurrency('GBP 22.00'))
        txn.manage_post()

        self.assertEqual(income.balance(effective=p3_dt), ZCurrency('GBP 0.00'))
        self.assertEqual(account.balance(effective=p3_dt), ZCurrency('GBP 0.00'))

        #
        # this is the big barf point
        #

        # first check that *any* delegation actually works ...
        self.assertEqual(self.ledger.Receivables.total(effective=(p2_dt,p3_dt)), ZCurrency('-GBP 22.00'))
        entry = control.Receivables
        self.assertEqual(entry.balance(effective=p3_dt), ZCurrency('GBP 0.00'))
        self.assertEqual(entry.total(effective=(p2_dt,p3_dt)), ZCurrency('-GBP 22.00'))
        self.assertEqual(entry.lastTransactionDate(), p3_dt-10)

        # then verify the call itself ...
        self.assertEqual(control.openingDate(p3_dt), floor_date(p2_dt + 1))
        self.assertEqual(control.openingBalance(p3_dt), ZCurrency('GBP 22.00'))
        self.assertEqual(control.balance(effective=p3_dt), ZCurrency('GBP 0.00'))
        
        # run another period end and see if the receivables balance carries over
        self.controller_tool.periodend_tool.manage_periodEnd(self.ledger, p3_dt)

        pinfoid = p3_dt.strftime('%Y-%m-%d')
        pinfo = ledger.periods._getOb(pinfoid)
        pinfoR = pinfo.Receivables
        pinfoL = pinfo.Ledger

        self.assertEqual(pinfoR.num_transactions, 1) # pmt

        self.assertEqual(pinfoL.gross_profit, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.net_profit, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.company_tax, ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.losses_forward, ZCurrency('GBP 0.00'))

        self.assertEqual(pinfoR.balance(account.getId()), ZCurrency('GBP 0.00'))
        self.assertEqual(pinfoL.balance(control.getId()), ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.periods.balanceForAccount(p3_dt, 'Receivables', account.getId()), ZCurrency('GBP 0.00'))

        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p1_dt - 1), EPOCH)
        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p2_dt - 1), ceiling_date(p1_dt))
        self.assertEqual(ledger.periods.lastClosingForLedger('Ledger', p3_dt - 1), ceiling_date(p2_dt))
        
        # ensure delete removes txns ...
        tids = pinfo.transactions
        self.assertEqual(len(self.ledger.Transactions(id=tids)), 2)

        self.controller_tool.periodend_tool.manage_reset(self.ledger)
        self.assertEqual(len(self.ledger.Transactions(id=tids)), 0)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestPeriodEnd))
    return suite
