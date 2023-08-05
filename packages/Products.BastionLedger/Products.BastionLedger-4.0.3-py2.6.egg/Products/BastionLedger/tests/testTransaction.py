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

from unittest import TestSuite, makeSuite
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date


class TestTransaction(LedgerTestCase):
    """
    verify transaction workflow
    """
    def testCreated(self):
        # the big all-in test ...
        ledger = self.ledger.Ledger
        self.assertEqual(ledger.meta_type, 'BLLedger')
        #self.failUnless(ledger.Accounts)
        #self.failUnless(ledger.Transactions)
        self.assertEqual(ledger.currencies, ['GBP'])
        self.failUnless(getattr(ledger, 'portal_workflow', False))

    def testAggregates(self):
        ledger = self.portal.ledger.Ledger
        self.failUnless(getattr(ledger, 'portal_workflow', False))
        dt = DateTime()
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(effective=dt)
	txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.total(), ZCurrency('GBP10.00'))
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.total(), ZCurrency('GBP 20.00'))
        self.assertEqual(txn.effective_date, floor_date(dt))

    def testWorkflow(self):
        ledger = self.portal.ledger.Ledger
        self.loginAsPortalOwner()
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(title='My Txn')
	txn = ledger._getOb(tid)

        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000002', -ZCurrency('GBP 10.00'))
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 10.00'))
        self.assertEqual(txn.creditTotal(), -ZCurrency('GBP 10.00'))
        self.assertEqual(txn.status(), 'complete')

        txn.content_status_modify(workflow_action='post')
        self.assertEqual(txn.status(), 'posted')

        # ensure it's not trashing the title (and effective date)
        self.assertEqual(txn.Title(), 'My Txn') 

        account = self.ledger.Ledger.A000001


        entry = account._getOb(tid)

        self.assertEqual(entry.status(), 'posted')
        self.assertEqual(entry.account, account.getId())
        self.assertEqual(entry.blAccount(), account)
        self.assertEqual(entry.blTransaction(), txn)
        self.assertEqual(entry.blLedger(), self.ledger.Ledger)
        self.assertEqual(entry.effective(), txn.effective())
        self.assertEqual(entry.amount, ZCurrency('GBP 10.00'))
        self.assertEqual(entry.isControlEntry(), False)

        unposted = entry.postingEntry()
        self.assertEqual(unposted.account, account.getId())
        self.assertEqual(unposted.blAccount(), account)
        self.assertEqual(unposted.blTransaction(), txn)
        self.assertEqual(unposted.blLedger(), self.ledger.Ledger)
        self.assertEqual(unposted.effective(), txn.effective())
        self.assertEqual(unposted.amount, ZCurrency('GBP 10.00'))

        # TODO - fix this ...
        #self.assertEqual(unposted.postedEntry(), entry)

        #
        # hmmm - AEDT timezone's inconsistently f**k these tests ...
        #
        #now = DateTime()
        #self.assertEqual(entry.asCSV(),
        #                 'T000000000001,Ledger,T000000000001,"My Txn","%s", GBP 10.00 ,Ledger/A000001,posted' % now.strftime('%Y/%m/%d'))
        #self.assertEqual(entry.asCSV(datefmt='%Y', curfmt="%0.1f"),
        #                 'T000000000001,Ledger,T000000000001,"My Txn","%s",10.0,Ledger/A000001,posted' % now.strftime('%Y'))

        self.assertEqual(list(account.objectIds()), [tid])
        self.assertEqual(account.entryItems(), [(tid, entry)])
        self.assertEqual(account.sum('A000002'), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum('A000002', debits=False), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum('A000002', credits=False), ZCurrency('GBP0.00'))
        self.assertEqual(account.entryValues(), [entry])
        now = DateTime(self.ledger.timezone)
        self.assertEqual(account.entryValues([now - 1, now + 1]), [entry])        
	self.assertEqual(account.balance(), ZCurrency('GBP 10.00'))

        self.assertEqual(entry, txn.entry(account.getId()))
                         
	self.assertEqual(self.ledger.Ledger.A000002.balance(), -ZCurrency('GBP 10.00'))
        
	txn.content_status_modify(workflow_action='reverse')
	self.assertEqual(txn.status(), 'reversed')
	self.assertEqual(self.ledger.Ledger.A000001.balance(), 0)
	self.assertEqual(self.ledger.Ledger.A000002.balance(), 0)

        reversal_txn = txn.referenceObject()
        self.assertEqual(reversal_txn.status(), 'postedreversal')

        # see if reset aint broke ...
        self.ledger.manage_reset()

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger
        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        temp_object = ledger.restrictedTraverse('portal_factory/BLTransaction/T000000000099')
        self.failUnless('T000000000099' in ledger.restrictedTraverse('portal_factory/BLTransaction').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'T000000000099')
        self.failUnless('T000000000099' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLTransaction/T000000000100')
        self.failUnless('T000000000100' in ledger.restrictedTraverse('portal_factory/BLTransaction').objectIds())
        temp_object.bltransaction_edit(title='Foo', effective=dt)
        self.assertEqual(ledger.Transactions(effective_date=dt)[0].title, 'Foo')
        self.failUnless('T000000000100' in ledger.objectIds())
        
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransaction))
    return suite
