#
#    Copyright (C) 2007-2009  Corporation of Balclutha. All rights Reserved.
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

import AccessControl
from BLEntry import BLEntry
from DateTime import DateTime
from utils import assert_currency, floor_date

# TODO clean this up ...
from Acquisition import aq_base
from BLGlobals import OPENING_BALANCE

def manage_addBLOpeningEntry(account, amount, effective=None, title='Opening Balance'):
    """
    add (or update) an opening balance entry
    """
    assert_currency(amount)

    ledger = account.blLedger().getId()
    account_url = '%s/%s' % (ledger, account.getId())

    id = account.generateId()

    # remove old cruft
    #try:
    #    entry = self._getOb(id)
    #    self._delObject(id)
    #except:
    #    pass
    
    entry = BLOpeningEntry(id, title, account_url, amount, '', ledger, effective or DateTime())
    account._setObject(id, entry)
    
    return entry
   

class BLOpeningEntry( BLEntry ):
    """
    An entry representing an opening balance

    This guy is *only* found in accounts, and there is should be an associated
    closing transaction which generated/updated it

    It will not appear in any BLEntry collection
    """
    meta_type = 'BLOpeningEntry'
    portal_type = 'BLEntry'

    def __init__(self, id, title, account, amount, ref='', ledger='', effective=None):
        BLEntry.__init__(self, id, title, account, amount, ref, ledger)
        self._effective_date = floor_date(effective or DateTime())

    def status(self): return 'posted'

    def _post(self):
        """
        write a copy of yourself to the account - changing id to txn id
        """
        pass


AccessControl.class_init.InitializeClass(BLOpeningEntry)
