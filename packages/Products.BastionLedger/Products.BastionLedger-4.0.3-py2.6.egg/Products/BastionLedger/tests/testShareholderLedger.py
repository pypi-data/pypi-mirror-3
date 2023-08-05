#
#    Copyright (C) 2002-2010  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionLedger.tests import LedgerTestCase

from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.BLInventory import manage_addBLPart


class TestShareholderLedger(LedgerTestCase.LedgerTestCase):

    def testCreated(self):
        # the big all-in test ...
        shareholders = self.ledger.Shareholders
        self.assertEqual(shareholders.meta_type, 'BLShareholderLedger')
        #self.failUnless(shareholders.Accounts)
        #self.failUnless(shareholders.Transactions)
        self.assertEqual(shareholders.currencies, ['GBP'])

    def testProcessInScope(self):
        self.failUnless(self.ledger.Shareholders.unrestrictedTraverse('dividend'))
        dividend = self.ledger.Shareholders.unrestrictedTraverse('dividend')
        self.assertEqual(dividend.aq_parent, self.ledger.Shareholders)

        # hmmm - this doesn't work ...
        #self.failUnless(self.ledger.Shareholders.dividend)
        

    def testProcesses(self):
        self.loginAsPortalOwner()
        shareholders = self.ledger.Shareholders
        shareholders.manage_addProduct['BastionLedger'].manage_addBLShareDefinition('ordinary', 
                                                                                    'Ordinary Shares', 
                                                                                    'GBP 1.00', 
                                                                                    1000,
                                                                                    DateTime('2010/01/01'))

        self.assertEqual(shareholders.ordinary.allotted(DateTime('2010/01/02')), 0)
        self.assertEqual(shareholders.shareDefinitionValues()[0], shareholders.ordinary)
        self.assertEqual(shareholders.getShareholdersWithShare('ordinary'), [])


        shareholders.manage_addProduct['BastionLedger'].manage_addBLShareholder(title='Warren Buffet')
        self.assertEqual(list(shareholders.accountIds()), ['S1000000'])

        shareholder = shareholders.S1000000
        self.assertEqual(shareholder.blLedger(), shareholders)

        self.assertEqual(shareholder.shareDefinitionValues(), [])

        shareholder.manage_addProduct['BastionLedger'].manage_addBLAllocation('ord01', 'ordinary', 1, DateTime(0))

        self.assertEqual(shareholder.allocationQuantity('ordinary'), 1)
        self.assertEqual(shareholder.shareDefinitionValues()[0], shareholders.ordinary)

        processes = self.controller_tool.processesForLedger(shareholders)
        self.assertEqual(processes, [self.controller_tool.dividend])

        # check that __bobo_traverse__ picks up the process
        div_process = shareholders.unrestrictedTraverse('dividend')

        self.assertEqual(div_process, processes[0])

        self.assertEqual(div_process.aq_parent, shareholders)

        request = self.app.REQUEST
        request['share_type'] = 'ordinary'
        request['total_amount'] = ZCurrency('GBP 1000.00')
        
        #div_process.run(share_type='ordinary',
        #                total_amount=ZCurrency('GBP 1000.00'))
        div_process.blprocess_run()

        self.assertEqual(shareholder.balance(), -ZCurrency('GBP 1000.00'))



    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Shareholders
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLShareholder/S222222')
        self.failUnless('S222222' in ledger.restrictedTraverse('portal_factory/BLShareholder').objectIds())
        S222222 = temp_object.portal_factory.doCreate(temp_object, 'S222222')
        self.failUnless('S222222' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLShareholder/S222223')
        self.failUnless('S222223' in ledger.restrictedTraverse('portal_factory/BLShareholder').objectIds())
        temp_object.blaccount_edit(title='Foo', 
                                   description='', 
                                   type='Asset', 
                                   subtype='Current Asset',
                                   currency='GBP',
                                   accno='2222')
        self.failUnless('2222' in ledger.Accounts.uniqueValuesFor('accno'))
        self.assertEqual(ledger.Accounts(accno='2222')[0].title, 'Foo')
        self.failUnless('S222223' in ledger.objectIds())

        # doCreate should create the real object
        dt = DateTime('2000/01/01')
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000099')
        self.failUnless('T000000000099' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        S222222 = temp_object.portal_factory.doCreate(temp_object, 'T000000000099')
        self.failUnless('T000000000099' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction/T000000000100')
        self.failUnless('T000000000100' in ledger.restrictedTraverse('portal_factory/BLSubsidiaryTransaction').objectIds())
        temp_object.bltransaction_edit(title='Foo', effective=dt)
        self.assertEqual(ledger.Transactions(effective_date=dt)[0].title, 'Foo')
        self.failUnless('T000000000100' in ledger.objectIds())
        
    def testPortalFactoryAllocations(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Shareholders
        ledger.manage_addProduct['BastionLedger'].manage_addBLShareholder(title='Warren Buffet')

        now = DateTime(self.ledger.timezone)

        temp_object = ledger.restrictedTraverse('portal_factory/BLShareDefinition/common')
        self.failUnless('common' in ledger.restrictedTraverse('portal_factory/BLShareDefinition').objectIds())
        temp_object.blshare_edit(title='Common',
                                 description='',
                                 face=ZCurrency('GBP 1'),
                                 allocated=1000,
                                 issue_date=now,
                                 voting_class='B')
        self.failUnless('common' in ledger.objectIds())

        self.assertEqual(ledger.common.fullyPaid(), True)

        account = ledger.S1000000

        temp_object = account.restrictedTraverse('portal_factory/BLAllocation/common111')
        self.failUnless('common111' in account.restrictedTraverse('portal_factory/BLAllocation').objectIds())
        temp_object.blallocation_edit(issue_date=now, 
                                      quantity=10, 
                                      definition='common', 
                                      percentage_paid=50.0)
        self.assertEqual(list(account.objectIds()), ['common111'])

        self.assertEqual(account.allocationValues('common', now), [account.common111])
        self.assertEqual(ledger.common.shareholders(), [account])
        self.assertEqual(ledger.common.allotted(), 10)
        self.assertEqual(ledger.common.fullyPaid(), False)
        self.assertEqual(ledger.votingClasses(), ['B'])

        self.assertEqual(account.getMemberIds(),['portal_owner'])
        self.assertEqual(ledger.voters(), ['portal_owner'])

    def testLedgerCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        temp_object = ledger.restrictedTraverse('portal_factory/BLShareholderLedger/bla')
        self.failUnless('bla' in ledger.restrictedTraverse('portal_factory/BLShareholderLedger').objectIds())
        temp_object.portal_factory.doCreate(temp_object, 'bla')
        self.failUnless('bla' in ledger.objectIds())


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestShareholderLedger))
    return suite
