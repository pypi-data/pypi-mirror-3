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
from Acquisition import aq_base
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import floor_date


class TestTaxTables(LedgerTestCase):
    """
    lightweight Zope-only tax table tests
    """
    def afterSetUp(self):
        LedgerTestCase.afterSetUp(self)
	self.controller_tool.manage_addProduct['BastionLedger'].manage_addBLTaxTable('company_tax')
        self.table = self.controller_tool.company_tax
        self.addRate = self.table.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord

    def testConstructed(self):
        self.assertEqual(self.table.indexes(), ['effective'])

    def testCanAddRate(self):
        self.addRate(0.35,DateTime('1980/01/01'))

        self.assertEqual(len(self.table.objectIds()),1)
        self.assertEqual(len(self.table._catalog), 1)

        table_rec = self.table.objectValues()[0]

        fields = table_rec.fields()
        fields.sort()
        self.assertEqual(fields, ['code', 'effective','rate',])

        self.assertEqual(self.table.getRate(DateTime('1999/01/01')), 0.35)

    def testRateOrdering(self):
        self.addRate(0.35,DateTime('1980/01/01'))
        self.addRate(0.34,DateTime('1981/01/01'))
        self.addRate(0.33,DateTime('1982/01/01'))

        recs = self.table.objectValues()
        
        self.assertEqual(min(recs).effective, DateTime('1980/01/01'))
        self.assertEqual(max(recs).effective, DateTime('1982/01/01'))

    def testMultiDimensional(self):
	self.controller_tool.manage_addProduct['BastionLedger'].manage_addBLTaxTable('personal_tax',
                                                                            'Personal Tax Rates',
                                                                            (('locale', 'FieldIndex'),))
        table = self.controller_tool.personal_tax
        self.assertEqual(table.title, 'Personal Tax Rates')
        self.assertEqual(table.dimensions(), ['locale'])

        addRate = table.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord
        addRate(0.10,DateTime('1980/01/01'), locale='gb')
        addRate(0.20,DateTime('1980/01/01'), locale='nz')
        addRate(0.10,DateTime('1981/01/01'), locale='gb')
        addRate(0.21,DateTime('1981/01/01'), locale='nz')

        table_rec = table.objectValues()[0]

        fields = table_rec.fields()
        fields.sort()
        self.assertEqual(fields, ['code', 'effective', 'locale', 'rate'])
        
        self.assertEqual(len(table.getTableRecords(DateTime('1980/06/01'),
                                                   locale='nz')),
                         1)
        self.assertEqual(len(table.getTableRecords(DateTime('1981/06/01'),
                                                   locale='nz')),
                         1)

    def testTieredAmounts(self):
	self.controller_tool.manage_addProduct['BastionLedger'].manage_addBLTaxTable('personal_tax',
                                                                            'Personal Tax Rates',
                                                                            (('amount', 'CurrencyIndex'),))
        table = self.controller_tool.personal_tax
        # we don't want to have to set up currencies ...
        table._catalog.indexes['amount']._updateProperty('base_currency', 'GBP')
        
        self.assertEqual(table.dimensions(), ['amount'])

        addRate = table.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord
        addRate(0.10,DateTime('1980/01/01'), amount=ZCurrency('GBP 10000'))
        addRate(0.20,DateTime('1980/01/01'), amount=ZCurrency('GBP 20000'))
        addRate(0.30,DateTime('1981/01/01'), amount=ZCurrency('GBP 30000'))
        addRate(0.40,DateTime('1981/01/01'), amount=ZCurrency('GBP 40000'))

        
        self.assertEqual(len(table.getTableRecords(DateTime('1980/06/01'),
                                                   amount={'query': ZCurrency('GBP 20000'),
                                                           'range':'max'})),
                         2)
        self.assertEqual(len(table.getTableRecords(DateTime('1981/06/01'),
                                                   amount={'query': ZCurrency('GBP 20000'),
                                                           'range':'min'})),
                         2)

        self.assertEqual(len(table.getTableRecords(DateTime('1981/06/01'),
                                                   amount={'query': (ZCurrency('GBP 18000'),
                                                                     ZCurrency('GBP 21000')),
                                                           'range':'minmax'})),
                         1)

        # this is a typical tiered tax table return entry ...
        self.assertEqual(map(lambda x: x.amount,
                             table.getTableRecords(DateTime('1980/06/01'),
                                                   sort_on='amount',
                                                   sort_order='asc')),
                         [ZCurrency('GBP 10000'),ZCurrency('GBP 20000')])

        self.assertEqual(map(lambda x: x.amount,
                             table.getTableRecords(DateTime('1981/06/01'),
                                                   sort_on='amount',
                                                   sort_order='asc')),
                         [ZCurrency('GBP 30000'),ZCurrency('GBP 40000')])


    def testCodes(self):
        self.assertEqual(self.table.taxCodes(), [])
        self.addRate(0.35, DateTime('2000/01/02'), 'C')
        self.assertEqual(self.table.taxCodes(), ['C'])
        self.assertEqual(self.table.taxCodes('2000/01/01'), [])

        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestTaxTables))
    return suite
