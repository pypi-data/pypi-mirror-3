#
#    Copyright (C) 2006-2008  Corporation of Balclutha. All rights Reserved.
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
from Testing import ZopeTestCase

from DateTime import DateTime
from Products.BastionLedger.utils import *

class TestUtils(ZopeTestCase.ZopeTestCase):

    def test_month_beginning_date(self):
        self.assertEqual(month_beginning_date('2006/05/20'), DateTime('2006/05/01'))

    def test_month_ending_date(self):
        self.assertEqual(month_ending_date('2006/05/20'), DateTime('2006/05/31'))
        # year end check ...
        self.assertEqual(month_ending_date('2006/12/20'), DateTime('2006/12/31'))
        # leap year check
        self.assertEqual(month_ending_date('2000/02/20'), DateTime('2000/02/29'))
        self.assertEqual(month_ending_date('2001/02/20'), DateTime('2001/02/28'))

    def testlastXDays(self):
        self.assertEqual(lastXDays(DateTime('2008/04/18'),3),
                         [DateTime('2008/04/16'), DateTime('2008/04/17'), DateTime('2008/04/18')])

    def testlastXMonthEnds(self):
        self.assertEqual(lastXMonthEnds(DateTime('2008/04/18'),3),
                         [DateTime('2008/02/29'), DateTime('2008/03/31'), DateTime('2008/04/30')])
        
    def testlastXMonthBegins(self):
        self.assertEqual(lastXMonthBegins(DateTime('2008/04/18'),3),
                         [DateTime('2008/02/01'), DateTime('2008/03/01'), DateTime('2008/04/01')])
        
        
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite
    
