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

import AccessControl, types, os, string, logging
from warnings import warn
from DateTime import DateTime
from App.Common import package_home
from Acquisition import aq_base
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from BLBase import ProductsDictionary, BSimpleItem

from Products.CMFCore.utils import getPackageName, minimalpath
from Products.CMFCore.DirectoryView import _dirreg, registerFileExtension, registerMetaType, \
     DirectoryView, DirectoryViewSurrogate, DirectoryRegistry, DirectoryInformation, \
     _generateKey, _findProductForPath
from Products.CMFCore.FSPythonScript import FSPythonScript
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.FSPropertiesObject import FSPropertiesObject
from Products.CMFCore import permissions
from OFS.Folder import Folder

from BLProcess import BLProcess
from BLSubsidiaryLedger import BLSubsidiaryLedger
from BLTransactionTemplate import BLTransactionTemplate
from BLTransaction import manage_addBLTransaction
from BLSubsidiaryTransaction import manage_addBLSubsidiaryTransaction
from BLEntryTemplate import BLEntryTemplate
from BLEntry import BLEntry
from Permissions import ManageBastionLedgers, OperateBastionLedgers

LOG = logging.getLogger('FSBLProcess')

class TransactionInformation( DirectoryInformation ):
    """ placeholder to resurrect further txn template stuff from filesystem"""

    def prepareContents(self, registry, register_subdirs=0):
        # hmmm need to strip and change id ...
        data, objects = DirectoryInformation.prepareContents(self, registry, register_subdirs)
            
        new_objects = []
        for ob in objects:
            id = ob['id']
            if id.endswith('.txn'):
                newid = ob['id'][:-4]
                new_objects.append( {'id':newid, 'meta_type':'FSBLTransactionTemplateView'} )
                data[newid] = FSBLTransactionTemplateView(newid, data[id]._dirpath)
                del data[id]
            else:
                new_objects.append(ob)
                
        #print "TransactionInformation::prepareContents(%s)\n%s" % (self.filepath, data)
        return data, tuple(new_objects)


class TxnTmplDirectoryInformation(DirectoryInformation):
    """
    A file system folder containing directores and Transaction Templates
    """
    def prepareContents(self, registry, register_subdirs=0):
        data, objects = DirectoryInformation.prepareContents(self, registry, register_subdirs)
        new_objects = []
        for ob in objects:
            id = ob['id']
            LOG.debug("%s %s" % (ob['id'], ob['meta_type']))
            if ob['meta_type'] == 'Filesystem Directory View' and id.endswith('.txn'):
                newid = ob['id'][:-4]
                new_objects.append( {'id':newid, 'meta_type':'FSBLTransactionTemplateView'} )
                data[newid] = FSBLTransactionTemplateView(newid, data[id]._dirpath)
                del data[id]
            else:
                new_objects.append(ob)
                
        #print "ProcessInformation::prepareContents(%s)\n%s" % (self.filepath, data)
        return data, tuple(new_objects)


class TransactionRegistry(DirectoryRegistry):
    """
    turns directories with a .txn prefix into ledger transaction objects
    """
    def __init__(self, dirreg):
        # ensure we stuff our stuff in the dirreg ...
        self.__dict__ = dirreg.__dict__

    def registerDirectory(self, name, _prefix, subdirs=1):
        if not isinstance(_prefix, types.StringType):
            _prefix = package_home(_prefix)
        filepath = os.path.join(_prefix, name)
        self.registerDirectoryByPath(filepath, subdirs)

    def registerDirectoryByPath(self, filepath, subdirs=1):
        fp = minimalpath(filepath)
        normfilepath = os.path.normpath(filepath)
        if normfilepath.endswith('.txn'):
            #print "registering TransactionInfo %s" % normfilepath
            self._directories[fp] = di = TransactionInformation(normfilepath, fp)
        else:
            #print "registering DirectoryInfo %s" % normfilepath
            self._directories[fp] = di = TxnTmplDirectoryInformation(normfilepath, fp)
        if subdirs:
            for entry in di.getSubdirs():
                e_filepath = os.path.join(normfilepath, entry)
                self.registerDirectoryByPath(e_filepath, subdirs)


class FSBLTransactionTemplateViewSurrogate( DirectoryViewSurrogate, BLTransactionTemplate ):

    meta_type = portal_type = 'FSBLTransactionTemplate'
    manage_options = BLTransactionTemplate.manage_options

    #manage_propertiesForm = BLTransactionTemplate.manage_propertiesForm
    
    default_page = 'bltransactiontemplate_view'
    icon = 'fsbltransaction_tpl.gif'
    index_html = __call__ = BLTransactionTemplate.__call__

    def __init__(self,  real, data, objects):
        DirectoryViewSurrogate.__init__(self, real, data, objects)
        BLTransactionTemplate.__init__(self, self.id, self.id)
    
AccessControl.class_init.InitializeClass( FSBLTransactionTemplateViewSurrogate )

class FSBLTransactionTemplateView( DirectoryView ):
    meta_type = portal_type = 'FSBLTransactionTemplate'

    def __init__(self, id, dirpath, fullname=None):
        DirectoryView.__init__(self, id, dirpath, fullname)
        #BLProcess.__init__(self, id, '')
        

    def __of__(self, parent):
        # this is our file system ZODB mixin ...
        info = _dirreg.getDirectoryInfo(self._dirpath)
        if info is not None:
            info = info.getContents(_dirreg)
        if info is None:
            data = {}
            objects = ()
        else:
            data, objects = info
            objects = list(objects)
            #for ob in self._objects:
            #    if ob not in objects:
            #        objects.append(ob)
            #for ob in self.objectValues():
            #    if ob.getId() not in data.keys():
            #        data[ ob.getId() ] = ob
        #print str(data)
        #print str(objects)
        s = FSBLTransactionTemplateViewSurrogate(self, data, objects)
        res = s.__of__(parent)
        return res


AccessControl.class_init.InitializeClass(FSBLTransactionTemplateView)
    

class FSBLEntryTemplate(FSPythonScript, BLEntryTemplate):
    """
    A File system BLEntryTemplate
    """
    meta_type = portal_type = 'FSBLEntryTemplate'

    # we can't edit this stuff - maybe we should be using a FSPropertiesObject here
    # instead of assignment via metadata ...
    property_extensible_schema__ = 0
    _properties = (
        {'id':'account', 'type':'string', 'mode':'r'},
        {'id':'currency', 'type':'string', 'mode':'r'},
        )
    
    manage_options = FSPythonScript.manage_options + (
        {'label':'Properties', 'action': 'manage_propertiesForm'},
        {'label':'View',       'action': 'view'},
        {'label':'Proxy',      'action': 'manage_proxyForm'},
        )

    default_page = 'blentrytemplate_view'
    index_html = __call__ = BLEntryTemplate.__call__

    def _createZODBClone(self):
        obj = BLEntryTemplate(self.getId(), '', '')
        obj.write(self.read())
        return obj

AccessControl.class_init.InitializeClass(FSBLEntryTemplate)

class FSBLTransactionTemplate(FSPythonScript):
    """
    A File system BLTransactionTemplate
    """
    meta_type = portal_type = 'FSBLTransactionTemplate'
    icon = 'fsbltransaction_tpl.gif'
    _params = ''
    _body = ''
    default_view = 'bltransactiontemplate_view'

    def _createZODBClone(self):
        obj = BLEntryTemplate(self.getId(), '', '')
        obj.write(self.read())
        return obj

AccessControl.class_init.InitializeClass(FSBLTransactionTemplate)



def createTransactionTemplateView(parent, reg_key, id=None):
    """ Add either a DirectoryView or a derivative object.
    """
    info = _dirreg.getDirectoryInfo(reg_key)
    if info is None:
        reg_key = _dirreg.getCurrentKeyFormat(reg_key)
        info = _dirreg.getDirectoryInfo(reg_key)
        warn('createDirectoryView() called with deprecated reg_key format. '
             'Support for old key formats will be removed in CMF 2.3. Please '
             'use the new key format <product>:<subdir> instead.',
             DeprecationWarning, stacklevel=2)
    if not id:
        id = reg_key.split('/')[-1]
    else:
        id = str(id)
    ob = FSBLTransactionTemplateView(id, reg_key)
    #
    # hmmm - manage_fixupOwnershipAfterAdd is dodgy ...
    #
    try:
        parent._setObject(id, ob)
    except AttributeError:
        pass
    
def addTransactionTemplateViews(ob, name, _prefix):
    """ Add a directory view for every subdirectory of the given directory.

    Meant to be called by filesystem-based code. Note that registerDirectory()
    still needs to be called by product initialization code to satisfy
    persistence demands.
    """
    if not isinstance(_prefix, basestring):
        package = getPackageName(_prefix)
    else:
        warn('addDirectoryViews() called with deprecated _prefix type. '
             'Support for paths will be removed in CMF 2.3. Please use '
             'globals instead.', DeprecationWarning, stacklevel=2)
        (package, name) = _findProductForPath(_prefix, name)

    reg_key = _generateKey(package, name)
    info = _dirreg.getDirectoryInfo(reg_key)
    if info is None:
        raise ValueError('Not a registered directory: %s' % reg_key)
    for entry in info.getSubdirs():
        entry_reg_key = '/'.join((reg_key, entry))
        createTransactionTemplateView(ob, entry_reg_key, entry)


# normal skins directory registration
registerFileExtension('ent', FSBLEntryTemplate)

registerMetaType('FSBLEntryTemplate', FSBLEntryTemplate)
registerMetaType('FSBLTransactionTemplate', FSBLTransactionTemplate)


# cruft to be removed after we've excised 'Processes' folders
from BLBase import BObjectManager as Folder
class CustomFolder(Folder): pass
class FSBLProcessView(DirectoryView): pass
