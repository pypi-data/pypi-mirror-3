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

import AccessControl, logging, os, string
from Acquisition import aq_base
from AccessControl.Permissions import view, view_management_screens, access_contents_information
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZScheduler.ZScheduleEvent import ZScheduleEvent

from BLBase import BObjectManager, ProductsDictionary
from Permissions import ManageBastionLedgers, OperateBastionLedgers

from zope.interface import implements
from interfaces.process import IProcess

manage_addBLProcessForm = PageTemplateFile('zpt/add_process', globals())
def manage_addBLProcess(self, id, title='', REQUEST=None):
    """
    Add a new BLProcess object with id *id*.
    """
    
    ob=BLProcess(id, title)
    self._setObject(id,  ob)
  
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class BLProcess( BObjectManager, ZScheduleEvent ):
    '''
    An ordered container of runnable objects that collectively define a process.
    The container manages the scheduling of the process dispatch.
    '''
    meta_type = portal_type = 'BLProcess'

    implements(IProcess)

    # tuple of hashes of parameter values ...
    parameterMap = ()

    manage_options = (
        { 'label' :  'Components',  'action':'manage_main',
          'help':('BastionLedger', 'process.stx') }, 
        { 'label' :  'View',  'action':'' },
        { 'label' :  'Properties',  'action':'manage_propertiesForm',
          'help':('OFSP', 'Properties.stx') }, 
        { 'label' :  'Schedule',    'action':'manage_scheduleForm',
          'help':('ZScheduler', 'event.stx') },
        { 'label' :  'Run',         'action':'manage_runForm' },
        ) + BObjectManager.manage_options[1:]

    manage_runForm = PageTemplateFile('zpt/process_run', globals())
    
    __ac_permissions__ = (
        (OperateBastionLedgers, ('manage_scheduleForm', 'manage_run')),
        (access_contents_information, ('accountsInContext', 'reports')),
        )

    default_page = 'blprocess_view'

    dontAllowCopyAndPaste = 0

    def __init__(self, id, title=''):
        ZScheduleEvent.__init__(self, id, title, id)

    def all_meta_types(self):
        return [
            ProductsDictionary('BLTransactionTemplate'),
            ProductsDictionary('Page Template'),
            ProductsDictionary('DTML Method'),
            ProductsDictionary('Script (Python)'),
            ]

    def Description(self):
        return self.description or self.__doc__

    def accountsInContext(self):
        """
        return accounts in the context of the process
        this is useful to apply objects defined in the BLProcess to the account using
        aqcuisition instead of having to pass parameters ...
        """
        return map( lambda x,y=self: x.__of__(y),
                    self.objectValues(self.account_types) )
    
    def manage_run(self, REQUEST=None, *args, **kw):
        """
        invoke the overridable run() function from ZMI
        """
        self.run(*args, **kw)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Process ran OK')
            return self.manage_runForm(self, REQUEST)

    def reportFilter(self, report):
        """
        an expression used to identify any reports in the Reports folder
        that would identify previous runs of the process
        """
        return False
    
    def reports(self):
	"""
	return a list of reports produced by prior runs of this process
	"""
	rf = getattr(self.aq_parent, 'Reports', None)
	if rf:
	    return filter(lambda x: self.reportFilter(x), rf.objectValues())
	return []

AccessControl.class_init.InitializeClass(BLProcess)

class BLProcesses( BObjectManager ):
    """
    Folder view for processes - this will eventually contain proxy objects
    with scheduling info about the actual process ...
    """
    meta_type = portal_type = 'BLProcesses'

    __ac_permissions__ = (
        (view_management_screens, ('manage_main',)),
        ) + BObjectManager.__ac_permissions__

    dontAllowCopyAndPaste = 0

    default_page = 'blprocesses_view'
    
    manage_options = (
        {'label':'Processes', 'action':'manage_main',
         'help':('BastionLedger', 'processes.stx') },
        ) + BObjectManager.manage_options[1:]
    
    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    def all_meta_types(self):
        return ( ProductsDictionary('BLProcess'), )


AccessControl.class_init.InitializeClass( BLProcesses )




