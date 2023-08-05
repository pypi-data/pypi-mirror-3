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

from ComputedAttribute import ComputedAttribute
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal
from Products.CMFDefault.PropertiesTool import PropertiesTool as BaseTool

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from AccessControl.class_init import InitializeClass

from OFS.PropertyManager import PropertyManager
from BLBase import BSimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces.properties import IPropertiesTool

from BTrees.OOBTree import OOBTree
from zope.interface import implements

_marker = []  # Create a new marker object.

class AccountPropertiesTool(PloneBaseTool, Folder, BaseTool):

    id = 'account_properties_tool'
    toolicon = 'tool.gif'

    meta_type = 'BLAccountPropertiesTool'
    
    meta_types = all_meta_types =  ((
        {'name' : 'Account Property Sheet',
         'action' : 'manage_addBLAccountPropertySheetForm'
         },
        ))

    implements(IPropertiesTool)

    manage_options = ((Folder.manage_options[0],) +
                        BaseTool.manage_options)

    manage_addBLAccountPropertySheetForm = PageTemplateFile('zpt/add_accounts_prop_sheet', globals())

    _security = ClassSecurityInfo()

    def title(self):
        """ Return BaseTool title
        """
        return BaseTool.title(self)

    title = ComputedAttribute(title, 1)

    def addPropertySheet(self, id, title='', propertysheet=None):
        """ Add a new PropertySheet
        """
        o = BLAccountsData(id, title)

        # copy the propertysheet values onto the new instance
        if propertysheet is not None:
            if not hasattr(propertysheet, 'propertyIds'):
                raise TypeError, 'propertysheet needs to be a PropertyManager'

            for property in propertysheet.propertyMap():
                pid=property.get('id')
                ptype=property.get('type')
                pvalue=propertysheet.getProperty(pid)
                if not hasattr(o, pid):
                    o._setProperty(pid, pvalue, ptype)

        self._setObject(id, o)


    def manage_addBLAccountPropertySheet(self, id, title='',
                                         propertysheet=None, REQUEST=None):
        """ Add a instance of a Property Sheet if handed a
        propertysheet put the properties into new propertysheet.
        """
        self.addPropertySheet(id, title, propertysheet)

        if REQUEST is not None:
            return self.manage_main()

    #
    #   'portal_properties' interface methods
    #
    _security.declareProtected(ManagePortal, 'editProperties')
    def editProperties(self, props):
        """Change portal settings
        """
        aq_parent(aq_inner(self)).manage_changeProperties(props)
        # keep this bit of hackery for backwards compatibility
        if props.has_key('smtp_server'):
            self.MailHost.smtp_host = props['smtp_server']
        if hasattr(self, 'propertysheets'):
            ps = self.propertysheets
            if hasattr(ps, 'props'):
                ps.props.manage_changeProperties(props)

    _security.declarePrivate('wrapAccount')
    def wrapAccount(self, account):
        id = account.getId()
        if not self._accounts.has_key(id):
            # Get a temporary member that might be
            # registered later via registerMemberData().
            temps = self._v_temps
            if temps is not None and temps.has_key(id):
                a = temps[id]
            else:
                base = aq_base(self)
                a = AccountData(base, id)
                if temps is None:
                    self._v_temps = {id:a}
                    if hasattr(self, 'REQUEST'):
                        # No REQUEST during tests.
                        self.REQUEST._hold(CleanupTemp(self))
                else:
                    temps[id] = a
        else:
            a = self._accounts[id]
        # Return a wrapper with self as containment and
        # the account as context.
        return a.__of__(self).__of__(account)

    _security.declarePrivate('registerAccountData')
    def registerAccountData(self, a, id):
        '''
        Adds the given account data to the _accounts dict.
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        '''
        self._accounts[id] = a

AccountPropertiesTool.__doc__ = BaseTool.__doc__

InitializeClass(AccountPropertiesTool)

class CleanupTemp:
    """Used to cleanup _v_temps at the end of the request."""
    def __init__(self, tool):
        self._tool = tool
    def __del__(self):
        try:
            del self._tool._v_temps
        except (AttributeError, KeyError):
            # The object has already been deactivated.
            pass


class BLAccountsData (PropertyManager, BSimpleItem):
    """
    A common base class for objects with configurable
    properties in a fixed schema.
    """
    icon = 'misc_/BastionLedger/accountdata'

    def __init__(self, id, title=''):
        self.id = id
        self.title = title
        self._properties = ()
        self._accounts = OOBTree()

    meta_type = 'BLAccountsData'
    property_extensible_schema__ = 1
    
    manage_options = ( PropertyManager.manage_options
                     + BSimpleItem.manage_options)


InitializeClass(BLAccountsData)


class AccountData(BSimpleItem):
    """
    Synonymous with CMF MemberData container
    """
    _security = ClassSecurityInfo()
    
    def __init__(self, tool, id):
        self.id = id
        # Make a temporary reference to the tool.
        # The reference will be removed by notifyModified().
        self._tool = tool

    _security.declarePrivate('notifyModified')
    def notifyModified(self):
        # Links self to parent for full persistence.
        tool = getattr(self, '_tool', None)
        if tool is not None:
            del self._tool
            tool.registerAccountData(self, self.getId())

    def getTool(self):
        return aq_parent(aq_inner(self))

    _security.declarePrivate('setProperties')
    def setProperties(self, mapping):
        '''Sets the properties of the account.
        '''
        # Sets the properties given in the MemberDataTool.
        tool = self.getTool()
        for id in tool.propertyIds():
            if mapping.has_key(id):
                if not self.__class__.__dict__.has_key(id):
                    value = mapping[id]
                    if type(value)==type(''):
                        proptype = tool.getPropertyType(id) or 'string'
                        if type_converters.has_key(proptype):
                            value = type_converters[proptype](value)
                    setattr(self, id, value)
        # Hopefully we can later make notifyModified() implicit.
        self.notifyModified()

    # XXX: s.b., getPropertyForMember(member, id, default)?

    _security.declarePublic('getProperty')
    def getProperty(self, id, default=_marker):

        tool = self.getTool()
        base = aq_base( self )

        # First, check the wrapper (w/o acquisition).
        value = getattr( base, id, _marker )
        if value is not _marker:
            return value

        # Then, check the tool and the user object for a value.
        tool_value = tool.getProperty( id, _marker )
        user_value = getattr( self.getUser(), id, _marker )

        # If the tool doesn't have the property, use user_value or default
        if tool_value is _marker:
            if user_value is not _marker:
                return user_value
            elif default is not _marker:
                return default
            else:
                raise ValueError, 'The property %s does not exist' % id

        # If the tool has an empty property and we have a user_value, use it
        if not tool_value and user_value is not _marker:
            return user_value

        # Otherwise return the tool value
        return tool_value

InitializeClass(AccountData)
