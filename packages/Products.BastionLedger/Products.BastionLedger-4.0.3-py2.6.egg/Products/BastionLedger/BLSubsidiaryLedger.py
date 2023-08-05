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

import AccessControl, types, operator, logging
from DateTime import DateTime
from Acquisition import aq_base
from OFS.ObjectManager import BeforeDeleteException
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.BastionBanking.ZCurrency import ZCurrency

from BLGlobals import EPOCH
from BLBase import *
from BLLedger import LedgerBase
from BLAccount import addBLAccount
from BLControlEntry import BLControlEntry
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Products.CMFCore import permissions
from utils import ceiling_date

from zope.interface import Interface, implements

from interfaces.tools import IBLLedgerToolMultiple

class ISubsidiaryLedger(Interface): pass

manage_addBLSubsidiaryLedgerForm = PageTemplateFile('zpt/add_subsidiaryledger', globals()) 
def manage_addBLSubsidiaryLedger(self, id, controlAccount, currencies, title='', REQUEST=None):
    """ a customer """

    try:
        # do some checking ...
        control = self.Ledger._getOb(controlAccount)
        assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
        assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."
        self._setObject(id, BLSubsidiaryLedger(id, title, control, currencies))
            
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

    return self._getOb(id)

def addBLSubsidiaryLedger(self, id, title='', REQUEST=None):
    """
    Plone-based entry - we set up a new account in the ledger for the control
    account if one's not passed in (which is unlikely)
    """
    gl = self.Ledger
    control = addBLAccount(gl, title='Control Account: %s' % title) # get next accno
    
    ledger = manage_addBLSubsidiaryLedger(self, id, control, gl.currencies, title)
    return id

class BLSubsidiaryLedger(LedgerBase):

    meta_type = portal_type = 'BLSubsidiaryLedger'

    implements(ISubsidiaryLedger, IBLLedgerToolMultiple)
    
    __ac_permissions__ = LedgerBase.__ac_permissions__ + (
        (OperateBastionLedgers,('controlAccount','controlEntry','manage_recalculateControl')),
        (ManageBastionLedgers, ('manage_changeControl',)),
        )

    account_types = ('BLSubsidiaryAccount',)
    transaction_types = ('BLSubsidiaryTransaction',)

    def __init__(self, id, title, control, currencies, account_id=100000, 
                 account_prefix='SL', txn_id=1, txn_prefix='ST'):

        # we also need to ensure this is a main GL account ...
        assert control.meta_type == 'BLAccount', \
               """Control account type must be BLAccount, not %s (%s)!""" % (control.meta_type,
                                                                             control.getId())
        
        LedgerBase.__init__(self, id, title, currencies, account_id, account_prefix,
                          txn_id, txn_prefix)
        self._control_account = control.getId()

    def manage_edit(self, title, description, txn_id, account_id, account_prefix,
                    txn_prefix, currencies, email='', instructions='', REQUEST=None):
        """
        update ordbook properties
        """
        # TODO - bodgy hack to ensure control account creation via Plone portal factories ...
        if self._control_account == '':
            self._control_account = self.REQUEST['control_account']
            addSubsidiaryLedger(self, None)

        return LedgerBase.manage_edit(self, title, description, txn_id, account_id, account_prefix,
                                      txn_prefix, currencies, email, REQUEST)

    def controlAccount(self):
        """
        return the ledger account which this account aggregates into
        """
        try:
            return self.Ledger._getOb(self._control_account)
        except:
            # hmmm maybe old-style
            try:
                return self.Ledger.Accounts._getOb(self._control_account)
            except:
                pass
        raise AttributeError, 'control account not found: %s' % self._control_account

    def controlEntry(self):
        """
        return the summary entry for this journal in the GL's control account
        """
        # TODO - we're having to do lazy creation because portal_factory is attempting to 
        # construct everything twice :(

        acc = self.controlAccount()
        try:
            entry =  self.controlAccount()._getOb(self.getId())
        except:
            self.manage_changeControl(self._control_account)
            entry =  self.controlAccount()._getOb(self.getId())
        #assert isinstance(entry, BLControlEntry), """doh - couldn't find control account entry: (%s)""" % self.controlAccount()
        return entry

    def manage_changeControl(self, control_account, effective=None, REQUEST=None):
        """
        go change the control account to a different account
        """
        # find and destroy ...
        try:
            controlEntry = self.controlEntry()
            control_id = controlEntry.getId()
            controlEntry.aq_parent._delObject(control_id)
        except:
            control_id = self.getId()
        
        self._control_account = control_account
        control = self.controlAccount()

        # create and add
        controlEntry = BLControlEntry(control_id,
                                      'Subsidiary Ledger (%s)' % control_id,
                                      control_account,
                                      self.total(currency=control.base_currency,
                                                 effective=(control.openingDate(),
                                                            effective or DateTime())))

        control._setObject(control_id, controlEntry)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Changed Control Account')
            return self.manage_main(self, REQUEST)

    def defaultCurrency(self):
        """ the currency of the control account"""
        return self.controlAccount().base_currency

    def createTransaction(self, effective=None, title='', entries=[]):
        """
        return a newly created BLTransaction
        """
        txn_id = self.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryTransaction(title=title,
                                                                                           effective=effective or DateTime(),
                                                                                           entries=entries)
        return self._getOb(txn_id)

    def manage_recalculateControl(self, effective=None, force=False, REQUEST=None):
        """
        Hmmm - 'useful' admin function - only for Manager permissions ...

        force means to recalculate from the very start instead of the opening balance record
        """
        try:
            controlEntry = self.controlEntry()
        except:
            # hmmm - it's not found - fall through
            controlEntry = None
            
        # automagically upgrade it ...
        if not isinstance(controlEntry, BLControlEntry):
            self.manage_changeControl(self._control_account)
            controlEntry = self.controlEntry()  # for status message ...
            
        control = self.controlAccount()
        opening = control.openingDate()

        #if opening and not force:
        #    controlEntry.amount = self.total(currency=control.base_currency,
        #                                      effective=(opening,effective))
        #else:
        #    controlEntry.amount = self.total(currency=control.base_currency,
        #                                      effective=effective)

        dt = ceiling_date(effective or self.lastTransaction().effective_date)
        controlEntry.amount = self.total(currency=control.base_currency,
                                          effective=dt)

        controlEntry._setEffectiveDate(dt)

        if REQUEST:
            REQUEST.set('management_view', 'Properties')
            REQUEST.set('manage_tabs_message',
                        "Recalculated %s" % str(controlEntry))
            return self.manage_propertiesForm(self, REQUEST)
                               

    def accountType(self):
        """
        indicate what type of account is assumed to go into this ledger
        """
        return self.controlAccount().type
    
    def _reset(self):
        """ remove all account/txn entries """
        LedgerBase._reset(self)
        # recreate control entry ...
        controlAccount = self.controlAccount()
        controlEntry = self.controlEntry()
        controlEntry.amount = ZCurrency(controlAccount.base_currency, 0)
        controlEntry._setEffectiveDate(EPOCH)

AccessControl.class_init.InitializeClass(BLSubsidiaryLedger)


def delSubsidiaryLedger(ob, event):
    #
    # remove the control account's subsidiary entry ...
    #
    try:
        ob.controlAccount()._delObject(ob.getId())
    except:
        # oh well - not there ...
        pass

