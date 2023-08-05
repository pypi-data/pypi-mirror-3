#
#    Copyright (C) 2008  Corporation of Balclutha. All rights Reserved.
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

from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.BLAssetRegister import BLAsset

dtrange = (DateTime('2006/01/01'), DateTime('2007/06/01'))

class TestDepreciationTool(LedgerTestCase):

    # TODO - fix up this timezone error!!!

    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
        self.asset = BLAsset('asset', 'Asset','', DateTime('2006/01/01'), ZCurrency('GBP1000'), 'A000006', 'Prime Cost', 1, [])
        # fudge timezone ...
        self.timezone = 'EST'

    def XtestPrimeCost(self):
        self.assertEqual(self.asset.depreciation(dtrange), ZCurrency('GBP1000'))

        self.asset._updateProperty('effective_life', 2)

        self.assertEqual(self.asset.depreciation(dtrange), ZCurrency('GBP500'))
        
    def XtestDiminishingRate(self):
        self.asset._updateProperty('depreciation_method', 'Diminishing Rate')

class TestAssetRegister(LedgerTestCase):

    def testTypeInfo(self):
        tinfo = self.portal.portal_types.getTypeInfo(self.ledger)
        self.failUnless(tinfo.allowType('BLAssetRegister'))

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        # doCreate should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAssetRegister/assets')
        self.failUnless('assets' in ledger.restrictedTraverse('portal_factory/BLAssetRegister').objectIds())
        assets = temp_object.portal_factory.doCreate(temp_object, 'assets')
        self.failUnless('assets' in ledger.objectIds())
 
        # document_edit should create the real object
        temp_object = ledger.restrictedTraverse('portal_factory/BLAssetRegister/assets2')
        self.failUnless('assets2' in ledger.restrictedTraverse('portal_factory/BLAssetRegister').objectIds())
        temp_object.blassetregister_edit(['Current Assets'])
        self.failUnless('assets2' in ledger.objectIds())


        temp_object = assets.restrictedTraverse('portal_factory/BLAsset/car')
        self.failUnless('car' in ledger.restrictedTraverse('portal_factory/BLAsset').objectIds())
        #car = temp_object.portal_factory.doCreate(temp_object, 'car')
        #self.failUnless('car' in ledger.objectIds())

        # eek - lots of parameters ...
        #temp_object.blasset_edit()
        #self.failUnless('car' in ledger.objectIds())

    def testDepreciation(self):
        dtrange = (DateTime('2006/01/01'), DateTime('2007/06/01'))

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLAssetRegister('Assets')
        register = self.ledger.Assets
        register.manage_addProduct['BastionLedger'].manage_addBLAsset(dtrange[0],
                                                                      ZCurrency('GBP1000.00'),
                                                                      'A000006',
                                                                      'Prime Cost',
                                                                      1,
                                                                      id='Widget')
        asset = register.Widget

        self.assertEqual(asset.totalCost(), ZCurrency('GBP 1000.00'))
        self.assertEqual(asset.depreciation(dtrange), ZCurrency('GBP1000.00'))
        self.assertEqual(register.depreciationAmount(dtrange), ZCurrency('GBP1000.00'))

        tid = register.manage_applyDepreciation(dtrange)
        self.assertEqual(tid, 'T000000000001')

        txn = self.ledger.Ledger._getOb(tid)

        self.assertEqual(txn.debitTotal(), ZCurrency('GBP1000.00'))

def test_suite():
    suite = TestSuite()
    #suite.addTest(makeSuite(TestDepreciationTool))
    suite.addTest(makeSuite(TestAssetRegister))
    return suite
