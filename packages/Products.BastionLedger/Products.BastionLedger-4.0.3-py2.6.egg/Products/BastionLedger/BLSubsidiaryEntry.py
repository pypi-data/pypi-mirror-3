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

import AccessControl, types
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Acquisition import aq_base

from Products.BastionBanking.ZCurrency import ZCurrency

from Permissions import ManageBastionLedgers
from BLEntry import BLEntry
#from BLAccount import BLAccount
from BLTransaction import BLTransaction
from utils import assert_currency
import logging

manage_addBLSubsidiaryEntryForm = PageTemplateFile('zpt/add_subsidiaryentry', globals()) 
def manage_addBLSubsidiaryEntry(self, account, amount, title='', id=None, REQUEST=None):
    """
    Add an entry - either to an account or a transaction ...
    """
    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    realself = self.this()
    assert realself.meta_type == 'BLSubsidiaryTransaction', \
           'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert realself.status() in ('', 'incomplete', 'complete'), \
           'Woa - invalid txn state %s' % str(realself)

    if not title:
        title = realself.title

    try:
        assert_currency(amount)
    except:
        try:
            amount = ZCurrency(amount)
        except:
            message = "Not a valid amount"
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return realself.manage_main(realself, REQUEST)
            raise ValueError, message

    if amount == 0:
        message = "Please post an amount"
        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', message)
            return realself.manage_main(realself, REQUEST)
        raise ValueError, message

    if not id:
        id = realself.generateId()
        
    if type(account) == types.StringType:
        account = getattr(self.blLedger(), account)

    id = realself.generateId()

    entry = BLSubsidiaryEntry(id, title, account.getId(), amount)
    realself._setObject(id, entry)

    if REQUEST is not None:
       return self.manage_main(self, REQUEST)

    return id

class BLSubsidiaryEntry( BLEntry ):
    """
    This class is to factor out choosing accounts from the subsidiary ledger for one
    side of the transaction.
    """
    meta_type = 'BLSubsidiaryEntry'
    portal_type = 'BLEntry'

    __ac_permission__ = BLEntry.__ac_permissions__ + (
        (ManageBastionLedgers, ('manage_postedAmount',)),
        )

    def isControlEntry(self): 
        return False

      
    def blLedger(self):
        """
        return the ledger which I am posted (or will be)
        """
	return self.aq_parent.aq_parent

    def manage_postedAmount(self, amount=None, REQUEST=None):
        """
        expert-mode fix up of incorrect fx rate affecting posting
        """
        if isinstance(amount, ZCurrency) and \
                amount.currency() == self.aq_parent.blLedger().controlAccount().base_currency:
            self.posted_amount = amount
        elif amount is None and getattr(aq_base(self), 'posted_amount',None):
            delattr(self, 'posted_amount')

        if REQUEST:
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLSubsidiaryEntry)
