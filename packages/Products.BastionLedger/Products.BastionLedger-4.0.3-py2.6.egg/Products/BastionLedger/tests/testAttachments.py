#
#    Copyright (C) 2010  Corporation of Balclutha. All rights Reserved.
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
from ZPublisher.HTTPRequest import FileUpload, FieldStorage

class TestAttachments(LedgerTestCase):
    """
    tests attachment round-tripping etc etc
    """

    def testRoundTrips(self):
        self.loginAsPortalOwner()
        receivables = self.ledger.Receivables
        receivables.manage_addProduct['BastionLedger'].manage_addBLOrderAccount(title='Acme Trading')
        account = receivables.A1000000

        orderdate = DateTime('2008/03/04')
        account.manage_addOrder(orderdate=orderdate)
        order = account.objectValues('BLOrder')[0]

        self.assertEqual(order.hasAttachments(), False)

        # hmmm - mimic HTTP upload file ...
        fp = open(os.path.join(os.path.dirname(__file__), 'data', 'Scan001.PDF'), 'rb')
        fs = FieldStorage(fp=fp,
                          environ={'CONTENT_TYPE':'application/pdf',
                                   #'CONTENT_TRANSFER_ENCODING':'base64',
                                   'CONTENT_DISPOSITION': 'attachment; filename="Scan001.PDF'},
                          keep_blank_values=1)
        fs.filename = 'Scan001.PDF'
        fu = FileUpload(fs)

        # hmmm - dunno why we need to publish the entire File IO api ...
        for attr in ('seek','tell','read'):
            setattr(fs, attr, getattr(fp, attr))
            setattr(fu, attr, getattr(fs, attr))

        order.manage_addAttachment(fu)

        self.assertEqual(order.hasAttachments(), True)
        attachment = getattr(order.attachments, 'Scan001.PDF')

        self.assertEqual(sha.new(order.attachmentPayload('Scan001.PDF')).hexdigest(), 
                         '87d458f604893ca4d27c99aae5d43642b19404da') # should agree with FS

        msg = email.message_from_string(order.blinvoice_template(email='a@b.com'))
        
        #eattach = msg.get_payload()[2]

        #self.assertEqual(sha.new(eattach).hexdigest(), 
        #                 '87d458f604893ca4d27c99aae5d43642b19404da') # should agree with FS

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAttachments))
    return suite
