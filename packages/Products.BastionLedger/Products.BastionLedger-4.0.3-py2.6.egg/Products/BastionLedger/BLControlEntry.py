#
#    Copyright (C) 2007-2010  Corporation of Balclutha. All rights Reserved.
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
from Acquisition import aq_base
from AccessControl.Permissions import access_contents_information
from BLEntry import BLEntry
from DateTime import DateTime
from Permissions import ManageBastionLedgers
from BLGlobals import EPOCH

from Products.BastionBanking.ZCurrency import ZCurrency

class BLControlEntry( BLEntry ):
    """
    An entry representing a summary amount from a subsidiary ledger

    This guy is *only* found in accounts, and there is *no* associated
    transaction
    """
    meta_type = 'BLControlEntry'
    portal_type = 'BLEntry'

    __ac_permissions__ = BLEntry.__ac_permissions__ + (
        (access_contents_information, ('lastTransactionDate', 'blEntry')),
        (ManageBastionLedgers, ('manage_recalculate',)),
        )

    manage_options = BLEntry.manage_options[0:2] + (
        {'label':'Recalculate', 'action':'manage_recalculate'},
        ) + BLEntry.manage_options[2:]

    _properties = (
        { 'id'   : 'title',    'type' : 'string',    'mode' : 'w' },
        { 'id'   : 'amount',   'type' : 'currency',  'mode' : 'r' },
        { 'id'   : 'ledger',   'type' : 'selection', 'mode' : 'r' , 'select_variable': 'ledgerIds'},
        )

    def isControlEntry(self):
        """
        returns if this is an entry for a control account
        """
        return True

    def effective(self):
        """
        hmmm - this guy is *always* effective, it's just his amount varies ...
        """
        return None

    def lastTransactionDate(self):
        """
        date from which this entry is valid - anything prior to this will
        require a recomputation from the underlying subsidiary ledger
        """
        dt = getattr(aq_base(self), '_effective_date', None)
        if dt:
            return dt.toZone(self.timezone)

        return EPOCH
    
    def blTransaction(self):
        """
	there is no transaction associated with a control entry - it's the summation
	of all the transactions in the subsidiary ledger
        """
        return None

    def blLedger(self):
        """
        return the ledger which I relate to (or None if I'm not yet posted)
        """
        # find by acquisition
        theledger = self.bastionLedger()

        try:
            return theledger._getOb(self.getId())     # id should be the same as ledger now as well ...
        except (KeyError, AttributeError):
            raise AttributeError, 'No BLLedger - BastionLedger=%s\n%s' % (theledger, self)

    def status(self): return 'posted'

    def balance(self, currency='', effective=None):
        """
        return the sum of all the entries from opening balance date til date specified
        """
        # _effective_date is the effective date of the latest subsidiary txn - the
        # latest date for which this 'cache' is good!!
        if not effective:
            return self.amount

        opening_dt = self.lastTransactionDate()

        if type(effective) in (types.ListType, types.TupleType):
            effective = max(effective)

        if  isinstance(effective, DateTime) and effective >= opening_dt:
            return self.amount
        
        # if we've deleted the ledger this control account is associated with we
        # don't want the thing to be borked ...
        try:
            ledger = self.blLedger()
            return ledger.total(currency=currency, effective=(EPOCH, effective))
        except:
            pass
        return self.zeroAmount()

    def total(self, currency='', effective=None):
        """
        return the value amount of activity between the date(s)
        """
        if type(effective) in (types.ListType, types.TupleType):
            max_dt = max(effective)
            min_dt = min(effective)
        elif isinstance(effective, DateTime):
            max_dt = effective
            # hmmm - we need a proper start date
            min_dt = EPOCH
        else:
            max_dt = DateTime()
            min_dt = EPOCH

        try:
            return self.blLedger().total(currency=currency,
                                         effective=(min_dt, max_dt))
        except AttributeError:
            # hmmm getLedger() failed - in subsidiary ledger setup
            return self.zeroAmount()

    def manage_recalculate(self, effective=None, force=False, REQUEST=None):
        """
        recompute our cached 'amount'
        """
        old = self.amount
        self.blLedger().manage_recalculateControl(effective or self.lastTransactionDate(), force)
        if REQUEST:
            REQUEST.set('manage_tabs_message',
                        'Recalculated control (%s->%s)' % (old, self.amount))
            return self.manage_main(self, REQUEST)

    def blEntry(self, currency='', effective=None):
        """
        return a BLControlEntry with the appropriate amount in our acquisition context

        we cannot return a genuine BLEntry because we are still not associated with
        any transaction ...
        """
        parent = self.aq_parent

        entry = BLControlEntry(self.getId(),
                               self.title,
                               self.account,
                               self.balance(currency, effective))

        if effective and type(effective) in (types.ListType, types.TupleType):
            entry._effective_date = max(effective)
        else:
            entry._effective_date = DateTime()

        return entry.__of__(parent)

AccessControl.class_init.InitializeClass(BLControlEntry)
