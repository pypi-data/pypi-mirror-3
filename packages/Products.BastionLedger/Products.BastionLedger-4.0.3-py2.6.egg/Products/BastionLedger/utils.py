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
import types

from email.MIMEMultipart import MIMEMultipart
from email.MIMEMessage import MIMEMessage
from email.MIMEText import MIMEText
from email.Message import Message

from Acquisition import aq_inner
from AccessControl import ModuleSecurityInfo
from DateTime import DateTime
from Products.Five.browser import BrowserView

_security = ModuleSecurityInfo()

def floor_date(dt):
    """
    return start of day date for dt - this is important for index comparisons and
    date range computations ...
    """
    if type(dt) in (types.TupleType, types.ListType):
        try:
            dt = min(dt)
        except:
            raise TypeError, dt
    if not isinstance(dt, DateTime):
        dt = DateTime(dt)
    return dt.earliestTime().toZone(dt.timezone())

def ceiling_date(dt):
    """
    return end of day date for dt - this is important for index comparisons and
    date range computations ...
    """
    if type(dt) in (types.TupleType, types.ListType):
        try:
            dt = max(dt)
        except:
            raise TypeError, dt
    if not isinstance(dt, DateTime):
        dt = DateTime(dt)
    return dt.latestTime().toZone(dt.timezone())

def month_beginning_date(dt):
    """
    return the DateTime of the first day of the month
    """
    if not isinstance(dt, DateTime):
        dt = DateTime(dt)
    return DateTime('%i/%s/01' % (dt.year(), dt.mm()))
                    
def month_ending_date(dt):
    """
    return the DateTime of the last day of the month
    """
    if not isinstance(dt, DateTime):
        dt = DateTime(dt)
    # find the first of the next month (thats easy) then deduct a day ...
    if dt.month() == 12:
        return DateTime('%i/01/01' % (dt.year() + 1)) - 1
    return DateTime('%i/%0.2i/01' % (dt.year(), dt.month() + 1)) - 1

def lastXDays(dt, x):
    """
    return the last x DateTime objects from the specified dt
    """
    if not isinstance(dt, DateTime):
        dt = DateTime(dt)
    dt = floor_date(dt)
    return map(lambda n: dt - n, range(x - 1, -1, -1))

def lastXMonthEnds(dt, x):
    """
    return the last x month-end dates
    """
    results = []
    end = month_ending_date(dt)
    start = month_beginning_date(dt)
    for n in range(0,x):
        results.append(end)
        end = start - 1
        start = month_beginning_date(end)
    results.reverse()
    return results

def lastXMonthBegins(dt, x):
    """
    return the last x month-end dates
    """
    return map(lambda x: x+1, lastXMonthEnds(dt, x+1)[:-1])

_security.declarePublic('floor_date', 'ceiling_date', 'month_beginning_date',
                        'month_ending_date', 'lastXDays', 'lastXMonthEnds',
                        'lastXMonthBegins')
_security.apply(globals())



def _mime_str(headers={}, body='', attachments=[], format='plain',
              charset_coding='iso-8859-1'):
    """
    return message string of a multipart MIME representation of the parameters
    attachments is a list of name,content-type,payload tuples
    """
    try:
        body = MIMEText(unicode(body,'utf-8').
                        encode(charset_coding),
                        format,charset_coding)
    except UnicodeEncodeError:
        body = MIMEText(body, format, 'utf-8')

    msg = MIMEMultipart()
    for k,v in headers.items():
        msg[k] = v

    msg.attach(body)

    for a in attachments:
        attachment = Message()
        attachment.set_payload(a[2])
        attachment.set_type(a[1])
        attachment.add_header('content-disposition', 'attachment', filename="%s" % a[0])
        msg.attach(attachment)

    return msg.as_string()

def assert_currency(obj):
    """
    there is some bizarre shit going on with reliability of isinstance in regard to ZCurrency
    objects so we're incorporating this thing here in one spot ...
    """
    try:
        if obj.__class__.__name__ == 'ZCurrency': return
    except:
        pass
    raise AssertionError, 'Invalid Amount: %s (type=%s)' % (obj, type(obj))

def registerLedgerDirectory(skins_dir, global_defs):
    """
    a special registrator which understands how to turn our .txn directories into
    FSBLTransactions

    we swap in our own functors and then swap them back out so as not to taint
    any subsequent product's expectations ...
    """
    import FSBLProcess
    from Products.CMFCore import DirectoryView
    from Products.CMFCore.DirectoryView import _dirreg

    _createDirectoryView = DirectoryView.createDirectoryView
    _addDirectoryViews = DirectoryView.addDirectoryViews
    _dirreg_save = _dirreg

    _dirreg = FSBLProcess.TransactionRegistry(_dirreg)


    DirectoryView.createDirectoryView = FSBLProcess.createTransactionTemplateView
    DirectoryView.addDirectoryViews = FSBLProcess.addTransactionTemplateViews

    _dirreg.registerDirectory(skins_dir, global_defs)

    _dirreg = _dirreg_save
    DirectoryView.createDirectoryView = _createDirectoryView
    DirectoryView.addDirectoryViews = _addDirectoryViews

# we don't want to create circular dependencies for introspection, so
# we're peaking under the hood in a nice little tail-recursive way
def isDerived(klassinfo, name):
    """
    klassinfo is a __class__ ...
    """
    if klassinfo.__name__ == name:
        return True
    for klass in klassinfo.__bases__:
        if isDerived(klass, name):
            return True
    return False

def id_cmp(me, other):
    """
    id comparison
    """
    my_id = me.getId()
    other_id = other.getId()
    if my_id > other_id:
        return 1
    elif my_id < other_id:
        return -1
    return 0
    
def effective_cmp(me, other):
    """
    effective date comparison
    """
    my_dt = me.effective()
    other_dt = other.effective()
    if my_dt > other_dt:
        return 1
    elif my_dt < other_dt:
        return -1
    return 0

class UtilView(BrowserView):
    """
    utility class for binding functions via zcml
    """
