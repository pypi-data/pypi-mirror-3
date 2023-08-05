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

import AccessControl, logging, string
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from Acquisition import aq_base, aq_inner
from BLBase import PortalContent
from BLAccount import BLAccount
from Permissions import OperateBastionLedgers
from Products.PageTemplates.PageTemplateFile import PageTemplateFile



manage_addCMFAccountForm = PageTemplateFile('zpt/add_cmfaccount', globals())
def manage_addCMFAccount(self, id, path, REQUEST=None):
    """
    Add a proxy for another account
    """
    try:
        account = self.unrestrictedTraverse(path)
    except:
	raise
    assert isinstance(account, BLAccount), \
           'Not a BLAccount: %s!' % account

    self._setObject(id, CMFAccount(id, path))
    if REQUEST:
	REQUEST.RESPONSE.redirect('%s/manage_workspace' % REQUEST['URL3'])
    return id


class CMFAccount(PortalContent):
    """
    Wrap a plone skin around a BastionLedger Account

    This will probably evolve to include an account property adornment
    tool synonymous to the MembershipTool

    Note this object ISN'T for account creation - this must be
    done from within the context of a BastionLedger ...

    This also provides safe read accessors for account display/formatting
    """
    meta_type = portal_type = 'CMFAccount'

    _security = ClassSecurityInfo()

    __ac_permissions__ = (
        (view, ('accountId', 'entries', 'balance')),
        (view_management_screens, ('manage_edit',)),
        (OperateBastionLedgers, ('blAccount',)),
    ) + PortalContent.__ac_permissions__

    manage_options = (
        {'label':'Account', 'action':'manage_account'},
        {'label':'View',       'action':'view'},
        ) + PortalContent.manage_options
    
    manage_account = PageTemplateFile('zpt/cmf_account', globals())
    
    def __init__(self, id, path):
        self.id = id
        self.path = path

    def manage_edit(self, path, REQUEST=None):
        """ """
        account = self.restrictedTraverse(path)
        if account and account.meta_type in ('BLOrderAccount',):    
            self.path = path
        else:
            msg = 'Invalid path'
            if REQUEST:
                REQUEST.set('manage_tabs_message', msg)
                return self.manage_main(self, REQUEST)
            raise AttributeError, msg

    def getAccountPath(self):
        """
        override in sub-classes to find underlying Ledger Account
        """
        return self.path

    def manage_redirect(self, REQUEST):
        """
        redirect user to underlying account
        """
	obj = self.unrestrictedTraverse(self.path)
        REQUEST.RESPONSE.redirect('%s/manage_main' % obj.absolute_url())

    def _blAccount(self, REQUEST=None):
        """
        cannot save this to a local volatile because this f**ks up acquisition
        necessary for underlying account methods, but we may think of something
        smarter in the future ...
        """
        # this may be a little dangerous ...
        return self.unrestrictedTraverse(self.getAccountPath())

    # hmmm - scripts need this ...
    blAccount = _blAccount
    
    def __getitem__(self, name):
        if  getattr(aq_base(self), name, None):
            return getattr(self, name)
        account = self._blAccount()
        if getattr(aq_base(account), name):
            return getattr(account, name).__of__(self)
        raise KeyError, name

    #
    # some popular account methods ...
    #
    # note that we could improve performance here by deciding which of those
    # need acquisition context and which don't (and therefore could delegate
    # to a cached account) ...
    #
    def accountId(self):
        return self._blAccount().getId()

    def entries(self, effective=None):
        return self._blAccount().entries(effective or DateTime())

    def balance(self, effective=None):
        return self._blAccount().balance(effective=effective or DateTime())

    def currency(self):
	return self._blAccount().base_currency

AccessControl.class_init.InitializeClass(CMFAccount)
