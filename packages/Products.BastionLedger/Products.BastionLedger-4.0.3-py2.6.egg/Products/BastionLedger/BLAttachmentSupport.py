#
#    Copyright (C) 2006-2010  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, base64
from StringIO import StringIO
from Acquisition import aq_base
from AccessControl.Permissions import view_management_screens, delete_objects, \
     use_mailhost_services, access_contents_information
from OFS.Image import Image, File
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BLBase import BSimpleItem, BObjectManager
from Permissions import OperateBastionLedgers
from utils import _mime_str, Message


class BLAttachmentSupport(BSimpleItem):
    """
    allow other extraneous supporting documentation to be attached to an object
    """

    __ac_permissions__ = BSimpleItem.__ac_permissions__ + (
        (access_contents_information, ('hasAttachments', 'attachmentValues', 
                                       'attachmentsAsAttachments')),
        (view_management_screens, ('manage_attachments',)),
        (delete_objects, ('manage_delAttachments',)),
        (use_mailhost_services, ('manage_emailAttachments',)),
        )

    manage_options = (
        {'label':'Attachments', 'action':'manage_attachments'},
        ) + BSimpleItem.manage_options

    manage_attachments = PageTemplateFile('zpt/attachments', globals())

    def manage_addAttachment(self, file, REQUEST=None):
        """
        """
        if not getattr(aq_base(self), 'attachments', None):
            self.attachments = BObjectManager('attachments')

        filename = file.filename
        id = filename[max(filename.rfind('/'), filename.rfind('\\'), filename.rfind(':'),)+1:]

        # go figure out if it's an Image or a File ...
        obj = File(id, id, file)
        if obj.content_type.startswith('image'):
            obj = Image(id, id, file)

        self.attachments._setObject(id, obj)

        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            return self.manage_attachments(self, REQUEST)

    def manage_delAttachments(self, ids=[], REQUEST=None):
        """
        """
        try:
            self.attachments.manage_delObjects(ids)
        except:
            pass
        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            return self.manage_attachments(self, REQUEST)

    def manage_emailAttachments(self, ids, email, REQUEST=None):
        """
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise

        subject = self.title_or_id()

        mailhost.send(_mime_str({'Subject':subject, 'From':self.email, 'To':email}, '',
                                map(lambda x: (x.getId(),x.getContentType(), x.data),
                                    filter(lambda x,ids=ids: x.getId() in ids,
                                           self.attachments.objectValues()))),
                      [email], self.email, subject)

        if REQUEST:
            REQUEST.set('management_view', 'Attachments')
            REQUEST.set('manage_tabs_message', 'Attachment(s) sent')
            return self.manage_attachments(self, REQUEST)
            
    def hasAttachments(self):
        """
        return whether or not attachments are present
        """
        return getattr(aq_base(self), 'attachments', None) is not None and len(self.attachments) > 0

    def attachmentValues(self):
        """
        """
        if getattr(aq_base(self), 'attachments', None):
            return self.attachments.objectValues()
        return []

    def attachmentsAsAttachments(self):
        """
        return text-based attachment formatted with email headers and base64-encoded
        """
        results = []
        for attachment in self.attachmentValues():
            a = Message()
            content_type = attachment.getContentType()
            data = attachment.data

            if content_type.startswith('text') and isinstance(data, str):
                a.set_payload(data, charset='iso-8859-1')
            else:
                p = StringIO()
                if isinstance(data, str):
                    p.write(data)
                else:
                    while data is not None:
                        p.write(data.data)
                        data = data.next
                a.set_payload(p.getvalue())

                encoded = base64.b64encode(p.getvalue())
                # break encoded data into 80 char chunks
                a.set_payload('\n'.join(map(lambda x: encoded[x*80:(x+1)*80],
                                            xrange((len(encoded)/80)+1))))
                a.add_header('Content-Transfer-Encoding', 'base64')

            a.set_type(content_type)
            a.add_header('Content-Disposition', 'attachment', filename="%s" % attachment.getId())
            results.append(a.as_string())

        return results

    def attachmentPayload(self, id):
        """
        the raw content of the attachment
        """
        attachment = self.attachments._getOb(id)

        data = attachment.data
        if isinstance(data, str):
            return data
        else:
            p = StringIO()
            while data is not None:
                p.write(data.data)
                data = data.next
            return p.getvalue()


AccessControl.class_init.InitializeClass(BLAttachmentSupport)
