#
#    Copyright (C) 2006-2011  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionBanking.ZCurrency import ZCurrency


class TestAccount(LedgerTestCase):
    """
    verify account processing
    """
    def testEmptyStuff(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.blLedger(), ledger)
        self.assertEqual(account.openingBalance(), ledger.zeroAmount())
        self.assertEqual(account.openingDate(), EPOCH)

        self.assertEqual(account.base_currency, 'GBP')
        self.assertEqual(account.isFCA(), False)

    def testGlobalTagStuff(self):
        tax_exp = self.ledger.Ledger.accountsForTag('tax_exp')[0]
        self.assertEqual(tax_exp.hasTag('tax_exp'), True)
        self.assertEqual(tax_exp.hasTag('tax_accr'), False)

    def testLocalTagStuff(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.hasTag('Whippee'), False)

        ledger.manage_addTag('Whippee', [account.accno])

        self.assertEqual(account.tags, ('Whippee',))
        self.failUnless('Whippee' in ledger.Accounts.uniqueValuesFor('tags'))

        self.assertEqual(account.hasTag('Whippee'), True)

        
    def testAddTag(self):
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.failIf('tag1' in ledger.Accounts.uniqueValuesFor('tags'))
        account.updateTags('tag1')
        self.failUnless('tag1' in ledger.Accounts.uniqueValuesFor('tags'))


    def testGlobalTagStuff(self):
        # we silently ignore tags defined at global (portal_bastionledger) level
        ledger = self.ledger.Ledger
        account = ledger.A000001

        self.assertEqual(account.tags, ())

        ledger.manage_addTag('bank_account', [account.accno])

        self.assertEqual(account.tags, ())
        self.failIf('bank_account' in ledger.Accounts.uniqueValuesFor('tags'))


    def testPostingStuff(self):
        now = DateTime(self.ledger.timezone)
        later = now + 5

        ledger = self.ledger.Ledger
        account = ledger.A000001

        ledger.manage_addTag('Whippee', [account.accno])

        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(effective=now)
	txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000002', '-GBP 10.00')
        
        txn.manage_post()

        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(effective=later)
	txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000002', '-GBP 10.00')
        
        txn.manage_post()

        self.assertEqual(account.balance(effective=now), ZCurrency('GBP 10.00'))
        self.assertEqual(account.balance(effective=later), ZCurrency('GBP 20.00'))
        self.assertEqual(account.debitTotal(effective=now), ZCurrency('GBP 10.00'))
        self.assertEqual(account.debitTotal(effective=[now+2, later]), ZCurrency('GBP 10.00'))
        self.assertEqual(account.creditTotal(effective=now), ZCurrency('GBP 0.00'))
        self.assertEqual(account.creditTotal(effective=now+2), ZCurrency('GBP 0.00'))

        self.assertEqual(len(account.objectItemsByDate(effective=(EPOCH, now))), 1)
        self.assertEqual(len(account.objectItemsByDate(effective=(now, later))), 2)

        self.assertEqual(len(account.entryValues((EPOCH, now))), 1)
        self.assertEqual(ledger.sum(tags='Whippee', effective=now), ZCurrency('GBP 10.00'))

        self.assertEqual(len(account.entryValues((EPOCH, later))), 2)
        self.assertEqual(ledger.sum(tags='Whippee', effective=later), ZCurrency('GBP 20.00'))

        self.assertEqual(len(account.entryValues((now+2, later))), 1)
        self.assertEqual(ledger.sum(tags='Whippee', effective=[now+2, later]), ZCurrency('GBP 10.00'))

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAccount/A222222')
        self.failUnless('A222222' in ledger.restrictedTraverse('portal_factory/BLAccount').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'A222222')
        self.failUnless('A222222' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAccount/A222223')
        self.failUnless('A222223' in ledger.restrictedTraverse('portal_factory/BLAccount').objectIds())
        temp_object.blaccount_edit(title='Foo', 
                                   description='', 
                                   type='Asset', 
                                   subtype='Current Asset', 
                                   currency='GBP',
                                   accno='2222')
        self.failUnless('2222' in ledger.Accounts.uniqueValuesFor('accno'))
        self.assertEqual(ledger.Accounts(accno='2222')[0].title, 'Foo')
        self.failUnless('A222223' in ledger.objectIds())

    def testTaxGroups(self):
        # checking persistence/non-taint of tax_codes dictionary
        self.loginAsPortalOwner()
        ledger = self.ledger.Ledger

        # our placebo
        self.assertEqual(ledger.A000001.tax_codes, {})

        acc = ledger.manage_addProduct['BastionLedger'].manage_addBLAccount('crap','AUD', type='Revenue', accno='1234',)

        self.assertEqual(acc.tax_codes, {})

        acc.manage_addTaxCodes('sales_tax', [])

        self.assertEqual(acc.tax_codes, {'sales_tax':[]})
        self.assertEqual(ledger.A000001.tax_codes, {})
        
        acc.manage_delTaxGroups(['sales_tax'])

        self.assertEqual(acc.tax_codes, {})
        self.assertEqual(ledger.A000001.tax_codes, {})

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAccount))
    return suite
