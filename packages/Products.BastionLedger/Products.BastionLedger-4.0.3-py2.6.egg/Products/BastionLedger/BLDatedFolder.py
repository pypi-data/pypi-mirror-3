#
#    Copyright (C) 2002-2010  Corporation of Balclutha. All rights Reserved.
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

# import stuff
import AccessControl
from AccessControl import ClassSecurityInfo
from StringIO import StringIO
from DateTime import DateTime, Timezones

# some other stuff
import Acquisition, re, string
from urllib import quote
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog
from BLBase import *
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager

DATEMAX=DateTime('9999/12/31')

from zope.interface import Interface, implements

class IDatedFolder(Interface): pass
class IDatedEvent(Interface): pass

def _generateEventId(btreefolder2):
    """ Generate an ID for BLDated Events """
    ob_count = btreefolder2._count()

    if ob_count == 0:
        return 'event_000001'

    # Starting point is the highest ID possible given the
    # number of objects in the JTracker
    good_id = None
    found_ob = None

    while good_id is None:
        try_id = 'event_%s' % string.zfill(str(ob_count), 6)

        if ( btreefolder2._getOb(try_id, None) is None and
             btreefolder2._getOb('event_%i' % ob_count, None) is None ):

            if found_ob is not None:
                # First non-used ID after hitting an object, this is the one
                good_id = try_id
            else:
                if try_id == 'event_000001':
                    # Need to special-case the first ID
                    good_id = try_id
                else:
                    # Go down
                    ob_count -= 1
        else:
            # Go up
            found_ob = 1
            ob_count += 1

    return good_id

class BLDatedFolder( BObjectManagerTree, PropertyManager, BSimpleItem ):
    """ A folder with an index on date - this is expected to be used to
    gather effective-dates static/process control information ...  """

    meta_type = 'BLDatedFolder'

    implements(IDatedFolder)
    _security = ClassSecurityInfo()
    _properties = (
        { 'id'   : 'title'  , 'type' : 'string' ,  'mode' : 'w'  },
        { 'id'   : 'tz'     , 'type' : 'selection' ,'mode': 'w',
          'select_variable': 'Timezones'},
        )
    
    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + \
                         PropertyManager.__ac_permissions__ + \
                         BSimpleItem.__ac_permissions__
    manage_options = BObjectManagerTree.manage_options
    manage_propertiesForm = PropertyManager.manage_propertiesForm

    _security.declarePublic('display_calendar')
    display_calendar = PageTemplateFile('zpt/calendar_view', globals())
    
    def __init__(self, id, title, tz):
        BObjectManagerTree.__init__(self, id, title)
        self.tz = tz
        self.catalog = ZCatalog( 'catalog', 'Catalog')
        cat = getattr(self, 'catalog')
    
        cat.addIndex('day', 'FieldIndex')
        for name in ('id', 'title', 'day'):
            cat.addColumn(name)

    _security.declarePublic('matrix')
    def matrix(self, date=None):
        if date == None:
            date = DateTime(self.tz)
        else:
            assert isinstance(date, DateTime), "date parameter is not a DateTime!"

        # get first day of month ...
        month = date.month()
        date = DateTime(date.year(), month, 1)
        
        # pad the first bit ...
        result = [ ('') for l in range(0, date.dow()) ]
        while date.month() == month:
            result.append(date)
            date = date + 1

        # pad the last bit ...
        quotient,remainder = divmod(len(result), 7)
        if remainder:
            result.extend([ ('') for l in range(0, remainder + 1) ])
        else:
            quotient -= 1

        # split it into weeks ...
        weeks = []
        for n in range(0, quotient + 1):
            weeks.append( (result[7 * n:7 * n + 7]) )

        return weeks
        
    _security.declarePublic('prev')
    def prev(self, date):
        if date.month() == 1:
            return "%s/%s/01" % (date.year() - 1, 12)
        return "%s/%s/01" % (date.year(), date.month() - 1)

    _security.declarePublic('next')
    def next(self, date):
        if date.month() == 12:
            return "%s/%s/01" % (date.year() + 1, 1)
        return "%s/%s/01" % (date.year(), date.month() + 1)

    _security.declarePublic('day_class')
    def day_class(self, day):
        if day.isCurrentDay():
            return "list-header"
        # Sunday ...
        if day.dow() == 0:
            return "sunday"
        return "list-element"

    _security.declarePublic('getDay')
    def getDay(self, day):
        #
        # day is a DateTime object
        # override this to do exciting things ...
        #
        return day.day()

        
    _security.declarePublic('getEventsForDay')
    def getEventsForDay(self, date):
        """
        return all the objects for a day.
        """
        day = DateTime(date.year(), date.month(), date.day())
        return map( lambda x: x.getObject(), self.catalog({'day':day}) )

    _security.declarePublic('Timezones')
    def Timezones(self):
        return Timezones()

    #
    # hmmm - proper rerouting for BTreeFolder ...
    #
    #_security.declareProtected('View management screens', 'manage_object_workspace')
    def manage_object_workspace(self, ids=(), REQUEST=None):
        '''Redirects to the workspace of the first object in
        the list.'''
        if ids and REQUEST is not None:
            REQUEST.RESPONSE.redirect( '%s/manage_workspace' % quote(ids[0]) )
        else:
            return self.manage_main(self, REQUEST)    
    
AccessControl.class_init.InitializeClass(BLDatedFolder)


class BLDatedEvent(PropertyManager, BSimpleItem):
    """
    this is the underlying class for stuff to be stored in the BLDatedFolder's sparse
    date array.

    the date is used by the BLDatedFolder's _setObject method
    to determine it's position in the folder hierarchy
    
    """
    _security = ClassSecurityInfo()
    _properties = (
        { 'id'   : 'title', 'type' : 'string' , 'mode' : 'w'},
        { 'id'   : 'day'  , 'type' : 'date'   , 'mode' : 'r'},
        )

    __ac_permissions__ = PropertyManager.__ac_permissions__ + BSimpleItem.__ac_permissions__
    
    manage_main = PropertyManager.manage_propertiesForm
    manage_main._setName('manage_main')
    manage_options = PropertyManager.manage_options + BSimpleItem.manage_options
    
    def __init__(self, id, title, day):
        self.id = id
        self.title = title
        assert isinstance(day, DateTime), 'Bad Date!'
        self.day = day


    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name=prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value=REQUEST.get(name, '')
                self._updateProperty(name, value)

        self.indexObject()

    _security.declareProtected('Change Properties', 'setDay')
    def setDay(self, day):
        assert isinstance(day, DateTime), "Incorrect type for day"
        self.day = day
        self.indexObject()
    
    def indexObject(self):
        """ Handle indexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = getattr(self, 'catalog')
            url = '/'.join(self.getPhysicalPath())
            cat.catalog_object(self, url)
        except:
            pass
        
    def unindexObject(self):
        """ Handle unindexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = getattr(self, 'catalog')
            url = '/'.join(self.getPhysicalPath())
            cat.uncatalog_object(url)
        except:
            pass
        
AccessControl.class_init.InitializeClass(BLDatedEvent)


def addDatedEvent(ob, event):
    ob.indexObject()

def delDatedEvent(ob, event):
    ob.unindexObject()
