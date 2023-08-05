#
#    Copyright (C) 2009  Corporation of Balclutha. All rights Reserved.
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
from Products.CMFCore.utils import getToolByName

class TestForecaster(LedgerTestCase.LedgerTestCase):

    def testPortalFactoryCreation(self):
        self.loginAsPortalOwner()
        ledger = self.ledger
        temp_object = ledger.restrictedTraverse('portal_factory/BLForecaster/bla')
        self.failUnless('bla' in ledger.restrictedTraverse('portal_factory/BLForecaster').objectIds())
        bla = temp_object.portal_factory.doCreate(temp_object, 'bla')
        self.failUnless('bla' in ledger.objectIds())

    def testIt(self):
        self.loginAsPortalOwner()

        ledger = self.ledger.Ledger

        self.ledger.manage_addProduct['BastionLedger'].manage_addBLForecaster()

        forecaster = self.ledger.Forecaster
        forecaster._updateProperty('account_ids', ('A000001', 'A000002'))

        dt = DateTime('2010/03/20')
                                   
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLTransaction(effective=dt)
	txn = ledger._getOb(tid)

        amt = ZCurrency('GBP 10')
        zero = ZCurrency('GBP 0.00')

        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', amt)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000002', -amt)
         
        txn.manage_post()

        forecasts = forecaster.forecasts(dt - 30, 2)

        february = DateTime('2010/02/28')
        march = DateTime('2010/03/31')

        self.assertEqual(forecasts[0], [february, march])

        acc = ledger.A000001                         

        self.assertEqual(acc.balance(effective=february), ZCurrency('GBP 0.00'))
        self.assertEqual(acc.balance(effective=march), amt)

        self.assertEqual(forecasts[1][0], [acc, None, zero, None, amt])

        forecaster.manage_editForecasts(({'account':'A00001',
                                          'amount': 'GBP 10.00',
                                          'date': february},))

        forecasts = forecaster.forecasts(dt - 30, 2)

        #self.assertEqual(forecasts[1][0], [acc, amt, zero, None, amt])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestForecaster))
    return suite

