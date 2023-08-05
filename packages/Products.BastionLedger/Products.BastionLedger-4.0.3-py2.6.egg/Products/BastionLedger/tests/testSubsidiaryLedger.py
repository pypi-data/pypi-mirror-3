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

from unittest import TestSuite, makeSuite
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date


class TestSubsidiaryLedger(LedgerTestCase):
    """
    verify transaction workflow
    """
    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        self.ledger.manage_addProduct['BastionLedger'].addBLSubsidiaryLedger('junk')
        self.sub = self.ledger.junk
        id = self.sub.manage_addProduct['BastionLedger'].addBLSubsidiaryAccount('bob')
        self.acc = self.sub._getOb(id)

    def testDefaultCurrency(self):
        self.assertEqual(self.sub.defaultCurrency(), 'GBP')

        
    def testCreated(self):
        # the big all-in test ...
        ledger = self.sub
        self.assertEqual(ledger.meta_type, 'BLSubsidiaryLedger')
        #self.failUnless(ledger.Accounts)
        #self.failUnless(ledger.Transactions)
        self.assertEqual(ledger.currencies, ['GBP'])
        self.failUnless(getattr(ledger, 'portal_workflow', False))

        self.assertEqual(ledger._control_account, 'A000054')
        self.assertEqual(ledger.controlAccount(), self.ledger.Ledger.A000054)


    def testWorkflow(self):
        ledger = self.sub
        self.loginAsPortalOwner()
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryTransaction(title='My Txn')
	txn = ledger._getOb(tid)

        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.status(), 'incomplete')

        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ZCurrency('GBP 10.00'))
        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 10.00'))
        self.assertEqual(txn.creditTotal(), -ZCurrency('GBP 10.00'))
        self.assertEqual(txn.status(), 'complete')

        txn.content_status_modify(workflow_action='post')
        self.assertEqual(txn.status(), 'posted')
        self.assertEqual(ledger.total(), -ZCurrency('GBP 10.00'))

        # ensure it's not trashing the title (and effective date)
        self.assertEqual(txn.Title(), 'My Txn') 

        account = self.ledger.Ledger.A000001

        entry = account._getOb(tid)

        self.assertEqual(entry.status(), 'posted')
        self.assertEqual(entry.account, account.getId())
        self.assertEqual(entry.blAccount(), account)
        self.assertEqual(entry.blTransaction(), txn)
        #self.assertEqual(entry.getLedger(), self.ledger.Ledger)
        self.assertEqual(entry.effective(), txn.effective())
        self.assertEqual(entry.amount, ZCurrency('GBP 10.00'))
        self.assertEqual(entry.isControlEntry(), False)

        now = DateTime(self.ledger.timezone)
        #self.assertEqual(entry.asCSV(),
        #                 'ST000000000001,junk,ST000000000001,"My Txn","%s"," GBP 10.00 ",Ledger/A000001,posted' % now.strftime('%Y/%m/%d'))
        #self.assertEqual(entry.asCSV(datefmt='%Y', curfmt="%0.1f"),
        #                 'ST000000000001,junk,ST000000000001,"My Txn","%s","10.0",Ledger/A000001,posted' % now.strftime('%Y'))

        self.assertEqual(list(account.objectIds()), [tid])
        self.assertEqual(account.entryItems(), [(tid, entry)])
        self.assertEqual(account.sum(self.acc.getId()), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum(self.acc.getId(), debits=False), -ZCurrency('GBP10.00'))
        self.assertEqual(account.sum(self.acc.getId(), credits=False), ZCurrency('GBP0.00'))
        self.assertEqual(account.entryValues(), [entry])
        self.assertEqual(account.entryValues([DateTime() - 1, DateTime() + 1]), [entry])        
	self.assertEqual(account.balance(), ZCurrency('GBP 10.00'))

        self.assertEqual(entry, txn.entry(account.getId()))
                         
	self.assertEqual(self.acc.balance(), -ZCurrency('GBP 10.00'))
        
	txn.content_status_modify(workflow_action='reverse')
	self.assertEqual(txn.status(), 'reversed')

        reversal_txn = txn.referenceObject()
        self.assertEqual(reversal_txn.status(), 'postedreversal')
       
	self.assertEqual(self.acc.balance(), 0)
	self.assertEqual(self.ledger.Ledger.A000001.balance(), 0)
        self.assertEqual(ledger.total(), -ZCurrency('GBP 0.00'))


    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.sub

        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryAccount/crap')
        self.failUnless('crap' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryAccount').objectIds())
        SL000002 = temp_object.portal_factory.doCreate(temp_object, 'SL000002')
        self.failUnless('SL000002' in ledger.objectIds())
 

        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000099')
        self.failUnless('T000000000099' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'T000000000099')
        self.failUnless('T000000000099' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000100')
        self.failUnless('T000000000100' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        temp_object.bltransaction_edit(title='Foo', effective=dt)
        self.assertEqual(ledger.Transactions(effective_date=dt)[0].title, 'Foo')
        self.failUnless('T000000000100' in ledger.objectIds())
        
    def testControlBalance(self):
        ledger = self.sub
        self.loginAsPortalOwner()
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryTransaction(title='My Txn',
                                                                                          effective=DateTime('2007/07/01'))
	txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(self.acc.getId(), -ZCurrency('GBP 10.00'))
        txn.content_status_modify(workflow_action='post')

        control = self.sub.controlEntry()
        self.assertEqual(control.effective(), None)
        self.assertEqual(control.lastTransactionDate(), DateTime('2007/07/01'))

        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/07/01')),
                         ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/07/02')),
                         ZCurrency('GBP 10.00'))

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/01')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/02')),
                         ZCurrency('-GBP 10.00'))

        self.assertEqual(ledger.total(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.total(effective=DateTime('2007/07/01')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.total(effective=DateTime('2007/07/02')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.total(effective=(DateTime('2006/06/30'), DateTime('2007/07/02'))), 
                         ZCurrency('-GBP 10.00'))
        
        self.assertEqual(control.balance(), ZCurrency('-GBP 10.00'))
        self.assertEqual(control.balance(effective=DateTime('2007/06/30')), ZCurrency('GBP 0.00'))
        self.assertEqual(control.balance(effective=DateTime('2007/07/01')), ZCurrency('-GBP 10.00'))
        self.assertEqual(control.balance(effective=DateTime('2007/07/02')), ZCurrency('-GBP 10.00'))
        self.assertEqual(control.balance(effective=(DateTime('2006/06/30'), DateTime('2007/07/02'))), 
                         ZCurrency('-GBP 10.00'))

        # make sure that it's all still kosher after a period end ...
        ledger.periods.addPeriodInfo(self.ledger.Ledger, DateTime('2006/07/01'), DateTime('2007/06/30'))

        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/07/01')),
                         ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/07/02')),
                         ZCurrency('GBP 10.00'))

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/01')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2007/07/02')),
                         ZCurrency('-GBP 10.00'))

        self.assertEqual(ledger.total(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.total(effective=DateTime('2007/07/01')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.total(effective=DateTime('2007/07/02')),
                         ZCurrency('-GBP 10.00'))
        
        # and another - this barfed before ...
        ledger.periods.addPeriodInfo(self.ledger.Ledger, DateTime('2007/07/01'), DateTime('2008/06/30'))

        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 00.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2008/06/30')),
                         ZCurrency('GBP 10.00'))
        self.assertEqual(ledger.Ledger.A000001.balance(effective=DateTime('2008/07/02')),
                         ZCurrency('GBP 10.00'))

        self.assertEqual(self.acc.balance(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2008/06/30')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(self.acc.balance(effective=DateTime('2008/07/02')),
                         ZCurrency('-GBP 10.00'))

        self.assertEqual(ledger.total(effective=DateTime('2007/06/30')),
                         ZCurrency('GBP 0.00'))
        self.assertEqual(ledger.total(effective=DateTime('2008/06/30')),
                         ZCurrency('-GBP 10.00'))
        self.assertEqual(ledger.total(effective=DateTime('2008/07/02')),
                         ZCurrency('-GBP 10.00'))
        
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubsidiaryLedger))
    return suite
