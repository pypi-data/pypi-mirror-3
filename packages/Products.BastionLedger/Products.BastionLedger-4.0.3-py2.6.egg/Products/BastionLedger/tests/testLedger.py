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
from Products.BastionLedger.BLAssociations import ASSOCIATIONS

class TestLedger(LedgerTestCase):
    """
    verify Ledger processing
    """
    def testDefaultCurrency(self):
        self.assertEqual(self.ledger.Ledger.defaultCurrency(), 'GBP')

    def testNoSearchResultsDups(self):
        # tests that indexes have been restored after copy ...
        ledger = self.ledger.Ledger
        self.assertEqual(ledger.Accounts(accno=('2155',)), [ledger.A000013])
    

    def testGlobalTags(self):
        ledger = self.ledger.Ledger

        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountsForTag('sales_tax')), ['A000013'])

    def testLocalTags(self):
        ledger = self.ledger.Ledger

        self.failUnless('crap' not in ledger.Accounts.uniqueValuesFor('tags'))

        # office furniture and equipment
        ledger.manage_addTag('crap', ['1820'])

        self.failUnless('crap' in ledger.Accounts.uniqueValuesFor('tags'))

        new_tags = ledger.associations()

        #self.assertEqual(len(filter(lambda x: not x['global'], new_tags)), 1)

        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountsForTag('crap')), ['A000006'])

    def testLocalAddInGlobal(self):
        ledger = self.ledger.Ledger
        
        self.failUnless('sales_tax' not in ledger.Accounts.uniqueValuesFor('tags'))
        ledger.manage_addTag('sales_tax', ['1820'])
        self.failUnless('sales_tax' not in ledger.Accounts.uniqueValuesFor('tags'))

    def testAccountSearchTagAware(self):
        ledger = self.ledger.Ledger
        self.assertEqual(map(lambda x: x.getId(),
                             ledger.Accounts(tags='sales_tax')), ['A000013'])

    def testAccountValues(self):
        ledger = self.ledger.Ledger
        self.assertEqual(len(ledger.accountValues()), 53)
        self.assertEqual(map(lambda x: x.getId(),
                             ledger.accountValues(tags='sales_tax')), ['A000013'])
        

    def testRenameTag(self):
        ledger = self.ledger.Ledger

        self.failUnless('crap' not in ledger.Accounts.uniqueValuesFor('tags'))

        ledger.manage_addTag('crap', ['1820'])
        ledger.manage_renameTags(['crap'], 'crap1')

        self.assertEqual(ledger.A000006.accno, '1820')
        self.failUnless('crap' not in ledger.A000006.tags)
        self.failUnless('crap1' in ledger.A000006.tags)

    def testVerifyVerifies(self):
        self.loginAsPortalOwner()
        self.assertEqual(self.ledger.verifyExceptions(), None)

    def testCopyPaste(self):
        self.loginAsPortalOwner()
        self.portal.manage_addProduct['OFSP'].manage_addFolder('copies')
        self.portal.copies.manage_pasteObjects(self.portal.manage_copyObjects('ledger'))
        self.failUnless(self.portal.copies.ledger)

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        temp_object = self.portal.restrictedTraverse('portal_factory/Ledger/new_ledger1')
        self.failUnless('new_ledger1' in self.portal.restrictedTraverse('portal_factory/Ledger').objectIds())
        new_ledger1 = temp_object.portal_factory.doCreate(temp_object, 'new_ledger1')
        self.failUnless('new_ledger1' in self.portal.objectIds())
 
        # document_edit should create the real object
        temp_object = self.portal.restrictedTraverse('portal_factory/Ledger/new_ledger2')
        temp_object.blledger_edit('Ledger 2', 'USD', 'EST')
        self.failUnless('new_ledger2' in self.portal.objectIds())
        

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestLedger))
    return suite
