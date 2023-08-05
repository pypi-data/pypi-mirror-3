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
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from Acquisition import aq_parent, aq_inner, aq_base
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.class_init import InitializeClass

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Ledger import Ledger

class LedgerTool(UniqueObject, PropertyManager, SimpleItem, ActionProviderBase):
    """
    This is a proxy for a ledger defined elsewhere in your Zope Hierarchy.  This
    allows you to use a single ledger across a group of Plone sites.
    """
    implements(IPublishTraverse)

    id = 'bastion_ledger'
    meta_type = 'BastionLedger Tool'
    meta_types = all_meta_types = ()

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
	(view, ('getLedger',)),
        ) + SimpleItem.__ac_permissions__ + ActionProviderBase.__ac_permissions__

    _properties = (
        {'id':'ledger', 'type':'selection', 'mode':'w',
         'select_variable':'ledgers'},
        )
    
    _actions = ()

    _security = ClassSecurityInfo()
    _security.declareObjectProtected(view)

    #
    #   ZMI methods
    #
    _security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/ledgertool_explain', globals())

    manage_options = ActionProviderBase.manage_options + (
        {'label':'Overview', 'action':'manage_overview'},
        ) + PropertyManager.manage_options + SimpleItem.manage_options

    def __init__(self, ledger='', path=''):
        self.ledger = ledger
        self._ledger_path = path

    def ledgers(self):
        return map(lambda x: x.getId(), self.superValues('Ledger'))

    def getLedger(self):
        """
        retrieve the underlying ledger
        """
        return getattr(self.aq_parent, self.__dict__['ledger'])

    def publishTraverse(self, REQUEST, name):
        """
        delegate to the designated ledger if named attribute not found
        """
        ob = getattr(self, name, None)
        if ob: return ob

        # upon setup, ledger may not be set ...
        if self.ledger:
            return getattr(self.getLedger(), name, None)
        
        return None

    def __getitem__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        # upon setup, ledger may not be set ...
        if self.ledger:
            ledger = getattr(self.getLedger(), name, None)
            if ledger:
                return ledger
        raise KeyError, name

InitializeClass(LedgerTool)


