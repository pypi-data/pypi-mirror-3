#
#    Copyright (C) 2007  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionBanking.ZCurrency import ZCurrency

class TestQuotationManager(LedgerTestCase):

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        self.loginAsPortalOwner()
        self.ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart('widget')
        self.widget = self.ledger.Inventory.widget
        ledger = self.ledger.Ledger
        self.widget.edit_prices('kilo', 1.5, 5,
                                ZCurrency('GBP20'),
                                ZCurrency('GBP10'),
                                ZCurrency('GBP10'),
                                ledger.accountsForTag('part_inv')[0].getId(),
                                ledger.accountsForTag('part_inc')[0].getId(),
                                ledger.accountsForTag('part_cogs')[0].getId())
        


    def testCreated(self):
        self.failUnless(self.ledger.quotes)
    
    def testAvailableParts(self):
        self.assertEqual(map(lambda x: x.getId(),
                             self.ledger.quotes.availableParts()), ['widget'])

    def testQuote(self):
        quotemgr = self.ledger.quotes
        quotemgr.manage_addProduct['BastionLedger'].manage_addBLQuote('crap')
        quote = quotemgr.crap

        self.assertEqual(quote.status(), 'pending')

        quote.manage_addProduct['BastionLedger'].manage_addBLOrderItem('widget')
        self.assertEqual(quote.getGross(), ZCurrency('GBP 20.00'))

        receivable = quote.manage_createAccount('Receivables')
        self.failUnless(self.ledger.Receivables.objectIds(), [])

        quote.manage_raiseOrder()
        
    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLQuoteManager/quotes1')
        self.failUnless('quotes1' in ledger.restrictedTraverse('portal_factory/BLQuoteManager').objectIds())
        quotes = temp_object.portal_factory.doCreate(temp_object, 'quotes1')
        self.failUnless('quotes1' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLQuoteManager/quotes2')
        self.failUnless('quotes2' in ledger.restrictedTraverse('portal_factory/BLQuoteManager').objectIds())
        temp_object.blquotemgr_edit(['Receivables'])
        self.failUnless('quotes2' in ledger.objectIds())

        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestQuotationManager))
    return suite
