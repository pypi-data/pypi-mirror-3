#
#    Copyright (C) 2007-2010  Corporation of Balclutha. All rights Reserved.
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


class TestPayroll(LedgerTestCase):
    """
    hmmm - we've got all the aussie skins ....
    """

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        now = self.now = DateTime(self.ledger.timezone)
        self.payroll = payroll = self.ledger.Payroll
        payroll.currencies = ['GBP']
        payroll.manage_addProduct['BastionLedger'].manage_addBLEmployee('me', 'GBP', now - 7)
        self.employee = payroll.E1000000
        
    
    def testCreated(self):
        # the big all-in test ...
        self.assertEqual(self.payroll.meta_type, 'BLPayroll')
        self.assertEqual(self.payroll.currencies, ['GBP'])
        self.assertEqual(self.employee.Title(), 'me')

    def testPersonalTaxTable(self):
        # hmmm - make sure we're playing with what we think we are ...

        personal_tax = self.portal.portal_bastionledger.personal_tax
        self.assertEqual(len(personal_tax.objectIds()), 4)
        self.assertEqual(personal_tax._catalog.indexes['amount'].base_currency,
                         'GBP')

        for rates in (
            personal_tax.getTableRecords(),
            personal_tax.getTableRecords(DateTime()),
            personal_tax.getTableRecords(DateTime(),
                                         sort_on='amount',sort_order='asc'),
            ):
            
            self.assertEqual(map(lambda x: x.amount, rates),
                             [ZCurrency('GBP10000'), ZCurrency('GBP20000'),
                              ZCurrency('GBP30000'), ZCurrency('GBP40000')])

    def testSalaryOverTier(self):
        self.employee.manage_edit_private(start_day = self.now - 7, salary = ZCurrency('GBP52000'))

        self.assertEqual(self.payroll.is_run(self.now), False)
        self.payroll.manage_payEmployees(['E1000000'], self.now)
        self.assertEqual(self.payroll.is_run(self.now), True)

        txn = self.payroll.transactionValues()[0]

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 1000'))
        # damn - no standardtemplate.pt ...
        #self.failUnless(employee.objectValues('BLPaySlip')[0].blemployee_payslip())

        tax_entry = filter(lambda x: x.ref=='20-tax', txn.objectValues())[0]
        self.assertEqual(tax_entry.amount, ZCurrency('-GBP207.69'))

    def testSalaryWithinTierTwo(self):
        self.employee.manage_edit_private(start_day = self.now - 7,
                                          salary = ZCurrency('GBP26000'))

        self.assertEqual(self.payroll.is_run(self.now), False)
        self.payroll.manage_payEmployees(['E1000000'], self.now)
        self.assertEqual(self.payroll.is_run(self.now), True)

        txn = self.payroll.transactionValues()[0]

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 500'))
        # damn - no standardtemplate.pt ...
        #self.failUnless(employee.objectValues('BLPaySlip')[0].blemployee_payslip())

        tax_entry = filter(lambda x: x.ref=='20-tax', txn.objectValues())[0]
        self.assertEqual(tax_entry.amount, ZCurrency('-GBP42.31'))

    def testSalaryWithinTierThree(self):
        self.employee.manage_edit_private(start_day = self.now - 7,
                                          salary = ZCurrency('GBP36000'))

        self.assertEqual(self.payroll.is_run(self.now), False)
        self.payroll.manage_payEmployees(['E1000000'], self.now)
        self.assertEqual(self.payroll.is_run(self.now), True)

        txn = self.payroll.transactionValues()[0]

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 692.31'))
        # damn - no standardtemplate.pt ...
        #self.failUnless(employee.objectValues('BLPaySlip')[0].blemployee_payslip())

        tax_entry = filter(lambda x: x.ref=='20-tax', txn.objectValues())[0]
        self.assertEqual(tax_entry.amount, ZCurrency('-GBP92.31'))



    def testSalaryUnderTier(self):
        self.employee.manage_edit_private(start_day = self.now - 7,
                                          salary = ZCurrency('GBP5200'))

        self.assertEqual(self.payroll.is_run(self.now), False)
        self.payroll.manage_payEmployees(['E1000000'], self.now)
        self.assertEqual(self.payroll.is_run(self.now), True)

        txn = self.payroll.transactionValues()[0]

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP 100'))
        # damn - no standardtemplate.pt ...
        #self.failUnless(employee.objectValues('BLPaySlip')[0].blemployee_payslip())

        self.assertEqual(filter(lambda x: x.ref=='20-tax', txn.objectValues()), [])

    def testPayslips(self):
        self.loginAsPortalOwner()
        self.employee.manage_edit_private(start_day = self.now - 7,
                                          salary = ZCurrency('GBP5200'))

        self.payroll.manage_payEmployees(['E1000000'], self.now)

        # verify payslip renders
        payslip = getattr(self.employee, self.now.strftime('%Y-%m-%d'))

        self.assertEqual(payslip.Title(), self.now.strftime('%Y-%m-%d'))

        # hmmm - this crashes with lost txn entry ...
        #payslip.blemployee_payslip()

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Payroll
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLEmployee/A222222')
        self.failUnless('A222222' in ledger.restrictedTraverse('portal_factory/BLEmployee').objectIds())
        A222222 = temp_object.portal_factory.doCreate(temp_object, 'A222222')
        self.failUnless('A222222' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLEmployee/A222223')
        self.failUnless('A222223' in ledger.restrictedTraverse('portal_factory/BLEmployee').objectIds())
        temp_object.blaccount_edit(title='Foo', 
                                   description='', 
                                   type='Asset', 
                                   subtype='Current Asset', 
                                   currency='GBP',
                                   accno='2222')
        self.failUnless('2222' in ledger.Accounts.uniqueValuesFor('accno'))
        self.assertEqual(ledger.Accounts(accno='2222')[0].title, 'Foo')
        self.failUnless('A222223' in ledger.objectIds())

    def testDeduction(self):
        self.loginAsPortalOwner()
        self.employee.restrictedTraverse('portal_factory/BLEntryTemplate/union_due')
        self.failUnless('union_due' in self.employee.restrictedTraverse('portal_factory/BLEntryTemplate').objectIds())

    # we've removed factory tool support for adding timesheets ...
    def XtestTimesheetSlot(self):
        self.loginAsPortalOwner()
        ledger = self.ledger.Payroll
        temp_object = ledger.restrictedTraverse('portal_factory/BLTimesheetSlot/sick')
        self.failUnless('sick' in ledger.restrictedTraverse('portal_factory/BLTimesheetSlot').objectIds())
        temp_object.bltimesheetperiod_edit(title='Sick', ratio=1.0, min_hrs=0.0, max_hrs=8.0, defaults=[0,0,0,0,0,0,0])
        self.failUnless('sick' in ledger.objectIds())

        
    def testLedgerCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        temp_object = ledger.restrictedTraverse('portal_factory/BLPayroll/bla')
        self.failUnless('bla' in ledger.restrictedTraverse('portal_factory/BLPayroll').objectIds())
        temp_object.portal_factory.doCreate(temp_object, 'bla')
        self.failUnless('bla' in ledger.objectIds())


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestPayroll))
    return suite
