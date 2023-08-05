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
from Products.BastionLedger.Ledger import manage_addLedger
from Products.BastionLedger.FSBLProcess import  TxnTmplDirectoryInformation, \
     TransactionInformation, FSBLTransactionTemplateViewSurrogate

class TestFSBLProcesses(LedgerTestCase.LedgerTestCase):

    def testMonkeyPatchedDirectoryRegistry(self):
        tmpl_path = 'BastionLedger/skins/bastionledger/blp_dividend_payment.txn'
        from Products.CMFCore.DirectoryView import _dirreg, DirectoryInformation
        dirinfo = _dirreg._directories

        self.assertEqual(dirinfo['BastionLedger/skins/bastionledger'].__class__.__name__, 
                         'TxnTmplDirectoryInformation')
        self.assertEqual(dirinfo[tmpl_path].__class__.__name__, 
                         'TransactionInformation')
        self.assertEqual(_dirreg.getDirectoryInfo(tmpl_path).__class__.__name__, 
                         'TransactionInformation')

        txntmpl = getattr(self.portal.portal_skins.bastionledger, 'blp_dividend_payment')
        self.assertEqual(txntmpl.__class__.__name__, 'FSBLTransactionTemplateViewSurrogate')

    def testShareholders(self):
        txntmpl = getattr(self.portal.portal_skins.bastionledger, 'blp_dividend_payment')
        ids = txntmpl.objectIds()
        ids.sort()
        self.assertEqual(ids, ['bank', 'shareholder'])

    def testOrderbook(self):
        txntmpl = getattr(self.portal.portal_skins.bastionledger, 'blp_order')
        entries = txntmpl.objectIds()
	entries.sort()
        self.assertEqual(entries, ['Account', 'COGS', 'Freight', 'Inventory', 'Sales', 'Tax'])

    def testPayroll(self):
        txntmpl = getattr(self.portal.portal_skins.bastionledger, 'blp_employee_payment')
        ids = txntmpl.objectIds()
        ids.sort()
        self.assertEqual(ids, ['gross', 'net', 'tax'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestFSBLProcesses))
    return suite

