#
#    Copyright (C) 2008 - 2011  Corporation of Balclutha. All rights Reserved.
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
from Acquisition import aq_inner,aq_parent
from DateTime import DateTime

from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase
from Products.BastionLedger.BLAssociations import ASSOCIATIONS
from Products.BastionBanking.ZCurrency import ZCurrency

associations = list(ASSOCIATIONS)
associations.sort()

class TestControllerTool(LedgerTestCase):
    """
    verify the controller tool looks adequate
    """

    def testControllerSetUp(self):
        self.failUnless(self.controller_tool.sales_tax)
        self.failUnless(self.controller_tool.personal_tax)
        self.failUnless(self.controller_tool.company_tax)
        self.failUnless(self.controller_tool.associations)
        self.failUnless(self.controller_tool.Ledger)

    def testAssociations(self):
        # this just verifies associations are OK - it's a sister test
        # to the testLedger.testGlobalTags ...
        tags = list(self.controller_tool.associations.objectIds())
        tags.sort()
        self.assertEqual(tags, associations)

        tags = map(lambda x: x.getId(),
                   self.controller_tool.associations.searchObjects(ledger='Ledger'))
        tags.sort()
        self.assertEqual(tags, associations)


    def testProcessAcquisitionContexts(self):
        shareholders = self.ledger.Shareholders

        processes = self.controller_tool.processesForLedger(shareholders)
        self.assertEqual(self.controller_tool.processesForLedger(shareholders),
                         [])

        shareholders.manage_addProduct['BastionLedger'].manage_addBLShareDefinition('ordinary',
                                                                                    'Ordinary Shares',
                                                                                    'GBP 1.00',
                                                                                    1000)

        self.assertEqual(self.controller_tool.processesForLedger(shareholders),
                         [self.controller_tool.dividend])


        div_process_id = 'dividend'

        # test __bobo_traverse__ and __getattr__
        #div_process = getattr(shareholders, div_process_id)
        div_process = shareholders.unrestrictedTraverse(div_process_id)
                           
        self.assertEqual(div_process.meta_type, 'BLDividendProcess')
        self.assertEqual(div_process.aq_parent, shareholders)
        self.assertEqual(aq_parent(aq_inner(div_process)), shareholders)
        self.assertEqual(div_process.aq_parent.aq_parent, self.ledger)

        #
        # hmmm - we can't get __getattr__ to work !!!
        #
        
        #div_process = getattr(shareholders, div_process_id)

        #self.assertEqual(div_process.meta_type, 'BLDividendProcess')
        #self.assertEqual(div_process.aq_parent, shareholders)
        #self.assertEqual(aq_parent(aq_inner(div_process)), shareholders)
        #self.assertEqual(div_process.aq_parent.aq_parent, self.ledger)
    
    def testYearEnd(self):
        self.assertEqual(self.controller_tool.yearEnd(DateTime('2009/06/29')), DateTime('2009/06/30'))
        self.assertEqual(self.controller_tool.yearEnd(DateTime('2009/07/01')), DateTime('2010/06/30'))


    def testCurrencyAdd(self):
        if not self.do_currencies:
            return

        self.assertEqual(self.controller_tool.addCurrencies(((ZCurrency('AUD50'), DateTime()), 
                                                             (ZCurrency('GBP10'), DateTime()),), 'AUD'),
                         ZCurrency('AUD75'))
        self.assertEqual(self.controller_tool.addCurrencies(((ZCurrency('GBP10'), DateTime()), 
                                                             (ZCurrency('AUD50'), DateTime()),), 'GBP'),
                         ZCurrency('GBP30'))

    def testCurrencyConvert(self):
        if not self.do_currencies:
            return

        self.assertEqual(self.controller_tool.convertCurrency(ZCurrency('AUD50'), DateTime(), 'GBP'),
                         ZCurrency('GBP20'))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestControllerTool))
    return suite
