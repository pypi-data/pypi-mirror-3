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

import AccessControl, types, logging
from AccessControl.Permissions import view_management_screens, view
from Products.CMFCore import permissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.PythonScript import PythonScript
from DateTime import DateTime
from OFS.PropertyManager import PropertyManager

from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES

from BLEntry import BLEntry
from BLAccount import BLAccount
from BLTransaction import BLTransaction
from Permissions import OperateBastionLedgers
from BLBase import BSimpleItem


manage_addBLEntryTemplateForm = PageTemplateFile('zpt/add_entrytmpl', globals()) 
def manage_addBLEntryTemplate(self, id, currency, title='', 
                               account=None, REQUEST=None):
    """
    Add an entry - either to an account or a transaction ...
    """

    self._setObject(id, BLEntryTemplate(id, title, currency, account))
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))

    return 0

def addBLEntryTemplate(self, id, title=''):
    """
    """
    manage_addBLEntryTemplate(self, id, self.defaultCurrency(), title)
    return id

class BLEntryTemplate( BSimpleItem, PythonScript, PropertyManager ):
    """
    This class provides meta-information to generate a BLEntry.

    The underlying PythonScript call function executes this script.

    The class is so-designed that absolutely ANY of the parameters can
    be calculated from whatever one has access to from a Python Script ...
    """
    meta_type = portal_type = 'BLEntryTemplate'
    __setstate__ = PythonScript.__setstate__
    _params = 'account=None,args=[],kw={}'
    default_page = 'blentrytemplate_view'
    __ac_permissions__ = PythonScript.__ac_permissions__ + (
        (view, ('blAccount', 'blAccountId', 'select_currency', 'select_account', 'getText')),
	(OperateBastionLedgers, ('generate',)),
        ) + PropertyManager.__ac_permissions__

    _properties = (
        { 'id':'title',    'type':'string',   'mode':'w' },
        { 'id':'currency', 'type':'selection','mode':'w', 'select_variable':'select_currency' },
        { 'id':'account',  'type':'selection','mode':'w', 'select_variable':'select_account' },
        )

    manage_options = ( PythonScript.manage_options[0], ) + \
                     PropertyManager.manage_options + \
                     PythonScript.manage_options[3:]

    def __init__(self, id, title, currency, account=None):
        PythonScript.__init__(self, id)
        self.title = title
        self.currency = currency
        self.account = account
        if account is None or account == '':
            stub = \
"""from Products.BastionLedger.BLSubsidiaryEntry import BLSubsidiaryEntry

return [ BLSubsidiaryEntry(account.getId(),
                           kw.get('title', script.getId()),
                           account.getId(),
                           ZCurrency(script.currency, 10.00),
                           script.getId()) ]
"""
        else:
            stub = \
"""from Products.BastionLedger.BLEntry import BLEntry

return [ BLEntry(script.account,
                 kw.get('title', script.getId()),
                 'Ledger/%s' % script.account,
                 ZCurrency(script.currency, 10.00),
                 script.getId()) ]
"""
        self.write("""
#
# this is a generic stub giving you complete programatic access to
# templatise transaction entries.
#
# the context is the BLTransaction object which will contain the BLEntry resulting
# from this call.  the container is the BLTransactionTemplate
#
# A BLEntry/BLSubsidiaryEntry is constituted from:
#   id   - you should NEVER change this unless you REALLY know what you are doing!
#   desc
#   path to account
#   amount
#   a reference
#
# This script should return a list (possibly empty) of BLEntry objects
#
from Products.BastionBanking.ZCurrency import ZCurrency
%s
""" % stub)

    generate = PythonScript.__call__
    def getText(self):
	"""
	need view perms on this for skins ...
	"""
        return self.read()

    def ZPythonScript_editAction(self, REQUEST, title, params, body):
        """ """
        PythonScript.ZPythonScript_editAction(self, REQUEST, title, self._params, body)

    def ZPythonScript_edit(self, params, body):
        PythonScript.ZPythonScript_edit(self, self._params, body)

    def blAccount(self):
        if self.account:
            return getattr(self.Ledger, self.account)
        #
        # get the first account on our path ...
        #
        try:
            while not isinstance(self, BLAccount):
                self = self.aq_parent
            return self
        except:
            LOG.error('blAccount() acquired %s' % self)
            raise

    def blAccountId(self):
        if self.account:
            return self.account
        return self.blAccount().getId()

    def select_currency(self):
        """ """
        return CURRENCIES

    def _updateProperty(self, name, value):
        """ """
        if name == 'account' and value == 'None':
            value = None
        PropertyManager._updateProperty(self, name, value)

    def select_account(self):
        """ Acquire a list of accounts... """
        l = [ None ]
        # need to force lazymap evaluation ....
        l.extend( list(self.Ledger.objectIds()) )
        return l

    def __cmp__(self, other):
        """
        provide order of execution for entries in a transaction template - ie by id ...
        """
        if not isinstance(other, BLEntryTemplate):
            return 1
        self_id = self.getId()
        other_id = other.getId()
        if self_id > other_id: return 1
        if self_id < other_id: return -1
        return 0
    
AccessControl.class_init.InitializeClass(BLEntryTemplate)
