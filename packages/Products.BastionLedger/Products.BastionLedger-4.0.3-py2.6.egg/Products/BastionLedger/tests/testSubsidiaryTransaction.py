#
#    Copyright (C) 2002-2011  Corporation of Balclutha. All rights Reserved.
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
from Products.BastionLedger.utils import floor_date


class TestSubsidiaryTransaction(LedgerTestCase):
    """
    verify transaction workflow
    """

    def testEntry(self):
        ledger = self.portal.ledger.Receivables
        ledger.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        dt = DateTime(self.ledger.timezone)
        tid = ledger.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryTransaction(effective=dt)
	txn = ledger._getOb(tid)
        txn.manage_addProduct['BastionLedger'].manage_addBLEntry('A000001', 'GBP 10.00')
        self.assertEqual(txn.total(), ZCurrency('GBP10.00'))
        txn.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry('A1000000', 'GBP -10.00')
        self.assertEqual(txn.total(), 0)

        self.assertEqual(txn.entry('A000001').amount, ZCurrency('GBP 10.00'))
        self.assertEqual(txn.entry('A000001', 'Ledger').amount, ZCurrency('GBP 10.00'))
        self.assertEqual(txn.entry('A1000000').amount,-ZCurrency('GBP 10.00'))
        self.assertEqual(txn.entry('A1000000', 'Receivables').amount,-ZCurrency('GBP 10.00'))
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubsidiaryTransaction))
    return suite
