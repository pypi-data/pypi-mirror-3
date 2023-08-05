#
#    Copyright (c) 2004-2008, Corporation of Balclutha
#    All rights reserved.
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
#

from unittest import TestSuite, makeSuite

from Products.BastionLedger.tests import LedgerTestCase

from Acquisition import aq_base
from Products.BastionBanking.ZCurrency import ZCurrency


class TestInventory(LedgerTestCase.LedgerTestCase):

    def afterSetUp(self):
        LedgerTestCase.LedgerTestCase.afterSetUp(self)
        self.ledger.Inventory.manage_addProduct['BastionLedger'].manage_addBLPart('widget')
        self.widget = self.ledger.Inventory.widget
        
    def testPriceEdit(self):
        # the big all-in test ...
        self.loginAsPortalOwner()

        ledger = self.ledger.Ledger
        self.widget.edit_prices('kilo', 1.5, 5,
                                ZCurrency('GBP10'),
                                ZCurrency('GBP20'),
                                ZCurrency('GBP10'),
                                ledger.accountsForTag('part_inv')[0].getId(),
                                ledger.accountsForTag('part_inc')[0].getId(),
                                ledger.accountsForTag('part_cogs')[0].getId())

        self.assertEqual(self.widget.sellprice, ZCurrency('GBP10'))
        self.assertEqual(self.widget.listprice, ZCurrency('GBP20'))
        self.assertEqual(self.widget.lastcost,  ZCurrency('GBP10'))


    def testPartContentStuff(self):
        self.assertEqual(self.widget.text_format, 'structured-text')

    def testPloneCtors(self):
        self.loginAsPortalOwner()
        inventory = self.ledger.Inventory

        id = inventory.invokeFactory(type_name='BLPart', id='widget22')
        self.assertEqual(id, 'widget22')
        
        id = inventory.invokeFactory(type_name='BLPartFolder', id='folder22')
        self.assertEqual(id, 'folder22')

    # hmmm - this seems to crash with a form-rendering error ...
    def XtestPortalFactoryPartCreation(self):
        self.loginAsPortalOwner()
        inv = self.ledger.Inventory

        temp_object = inv.restrictedTraverse('portal_factory/BLPart/widget111')
        self.failUnless('widget111' in inv.restrictedTraverse('portal_factory/BLPart').objectIds())

        temp_object.blpart_edit("kg", 0.0, 20.0, ZCurrency('GBP 20'), ZCurrency('GBP 20'),
                                ZCurrency('GBP 10'), 'A000005','A000023','A000030')

        self.failUnless('widget111' in inv.objectIds())
        
    def testPortalFactoryPartFolderCreation(self):
        self.loginAsPortalOwner()
        inv = self.ledger.Inventory

        temp_object = inv.restrictedTraverse('portal_factory/BLPartFolder/widgets111')
        self.failUnless('widgets111' in inv.restrictedTraverse('portal_factory/BLPartFolder').objectIds())

        temp_object.folder_edit("Widgets", "these are widgets", id='widgets111')

        self.failUnless('widgets111' in inv.objectIds())
        
    def testCanAddPartNamedLedger(self):
        self.loginAsPortalOwner()
        inv = self.ledger.Inventory
        inv.manage_addProduct['BastionLedger'].manage_addBLPart('Ledger')
        

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestInventory))
    return suite
