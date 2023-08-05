#
#    Copyright (C) 2002-2008  Corporation of Balclutha. All rights Reserved.
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
from Products.CMFCore.utils import getToolByName

class TestBastionLedger(LedgerTestCase.LedgerTestCase):

    def testFromDefault(self):
        #manage_addLedger(self.app, 'ledger', 'default', 'test ledger', 'AUD')
        ledger = self.ledger
        self.failUnless(ledger)
	self.checkCreated(ledger)


    def checkCreated(self, ledger):
        # f**k knows why these guys behave like ghosts!!
        ledgers = ledger.objectIds()
        self.failUnless('Ledger' in ledgers)
        self.failUnless('Receivables' in ledgers)
        self.failUnless('Payables' in ledgers)
        self.failUnless('Inventory' in ledgers)
        self.failUnless('Payroll' in ledgers)
        self.failUnless('Shareholders' in ledgers)

    def testTags(self):
        ledger = self.ledger.Ledger
        for tag in ('part_cogs', 'part_inc', 'part_inv', 'order_payments', 'bank_account',
                    'payables', 'receivables', 'sales_tax', 'wages', 'dividend'):
            self.failUnless(ledger.accountsForTag(tag))

    def testWorkflows(self):
        wfs = getToolByName(self.getPortal(), 'portal_workflow').objectIds()
        self.failUnless('bltransaction_workflow' in wfs, )
        self.failUnless('blorder_workflow' in wfs)

    def testPortalTypes(self):
        pts = getToolByName(self.getPortal(), 'portal_types').objectIds()
        for t in ('Ledger', 'BLAccount', 'BLTransaction', 'BLSubsidiaryTransaction',
                  'BLLedger', 'CMFAccount', 'BLInventory', 'BLPartFolder', 'BLPart',
                  'BLOrderBook', 'BLOrderAccount', 'BLOrder', 'BLShareholderLedger',
                  'BLShareholder', 'BLDividendAdvice', 'BLPayroll', 'BLEmployee'):
            self.failUnless(t in pts, t)
        
    def testLedgerDelete(self):
        # testing cascading deletes don't stop us from removing a ledger at top level
        self.loginAsPortalOwner()
        self.portal.manage_delObjects('ledger')
        self.failUnless(1)
    
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBastionLedger))
    return suite

