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
from DateTime import DateTime
from Acquisition import aq_base
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ZCurrency import ZCurrency
from BLBase import ProductsDictionary
from utils import assert_currency
from BLTransaction import BLTransaction
from Permissions import OperateBastionLedgers


manage_addBLSubsidiaryTransactionForm = PageTemplateFile('zpt/add_subsidiarytransaction', globals()) 
def manage_addBLSubsidiaryTransaction(self, id='', title='', effective=None,
                                      ref=None, entries=[], REQUEST=None):
    """ add a subsidiary ledger transaction """

    #realself = self.this()
    #try:
    #    # f**ked up cyclic dependency resolution ...
    #    assert isinstance(realself.aq_parent, BLSubsidiaryLedger) and \
    #           realself.meta_type == 'BLTransactions', \
    #           """eek this isn't a BLTransactions within a BLSubsidiaryLedger (%s|%s)""" % (
    #        realself.aq_parent.meta_type, self.meta_type
    #        )
    #except NameError:
    #    from BLSubsidiaryLedger import BLSubsidiaryLedger
    #    assert isinstance(realself.aq_parent, BLSubsidiaryLedger) and \
    #           realself.meta_type == 'BLTransactions', \
    #           """eek this isn't a BLTransactions within a BLSubsidiaryLedger (%s|%s)""" % (
    #        realself.aq_parent.meta_type, self.meta_type
    #        )
        
    if ref:
        try:
            ref = '/'.join(ref.getPhysicalPath())
        except:
            pass

    # portal_factory needs this to be settable...
    if not id:
        id = str(self.nextTxnId())

    effective = effective or DateTime()
    if type(effective) == types.StringType:
        effective = DateTime(effective)
    effective.toZone(self.timezone)

    self._setObject(id, BLSubsidiaryTransaction(id, title, effective, ref))

    txn = self._getOb(id)

    # don't do entries with blank amounts ...
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        try:
            assert_currency(entry.amount)
        except:
            entry.amount = ZCurrency(entry.amount)
        if entry.get('credit', False):
            entry.amount = -abs(entry.amount)
        if entry.subsidiary:
            try:
                manage_addBLSubsidiaryEntry(txn, entry.account, entry.amount, entry.title)
            except NameError:
                # doh - more cyclic dependencies ...
                from BLSubsidiaryEntry import manage_addBLSubsidiaryEntry
                manage_addBLSubsidiaryEntry(txn, entry.account, entry.amount, entry.title)
        else:
            try:
                manage_addBLEntry(txn, entry.account,entry.amount, entry.title)
            except NameError:
                # doh - more cyclic dependencies ...
                from BLEntry import manage_addBLEntry
                manage_addBLEntry(txn, entry.account,entry.amount, entry.title)

    # figure out the sorry (or otherwise) state of the transaction
    txn.setStatus()

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % txn.absolute_url())

    return id


def addBLSubsidiaryTransaction(self, id, title=''):
    """
    Plone constructor
    """
    id =  manage_addBLSubsidiaryTransaction(self, id=id, title=title)
    return id

class BLSubsidiaryTransaction( BLTransaction ):

    meta_type = portal_type = 'BLSubsidiaryTransaction'

    def filtered_meta_types(self, user=None):
        """ """
        if self.status() in ['incomplete', 'complete']:
            return [ ProductsDictionary('BLEntry'),
                     ProductsDictionary('BLSubsidiaryEntry') ]
	return[]

    def _setObject(self, id, object, Roles=None, User=None, set_owner=1):
        #
        # auto-control the acceptable debit/credit sides to this ledger ...
        #
        assert object.meta_type in ('BLEntry', 'BLSubsidiaryEntry'), \
               "Must be derivative of BLEntry!"

	control = self.blLedger().controlAccount()
        assert object.account != 'Ledger/%s' % control.getId(), \
               "Cannot transact against the Control Account - %s (%s)" % (control.prettyTitle(), str(self))

        BLTransaction._setObject(self, id, object, Roles, User, set_owner)
        self.setStatus()

    def createEntry(self, account, amount, title=''):
        """
        """
        if self.blLedger().getId() == 'Ledger':
            self.manage_addProduct['BastionLedger'].manage_addBLEntry(account, amount, title)
        # hmmm - we might want to verify the account exists here or in Ledger etc etc ...
        self.manage_addProduct['BastionLedger'].manage_addBLSubsidiaryEntry(account, amount, title)

    def entries(self):
        """
        allow ttw with this comment
        """
        return self.objectItems(['BLEntry', 'BLSubsidiaryEntry'])

    def entryItems(self):
        return self.objectItems(['BLEntry', 'BLSubsidiaryEntry'])

    def entryValues(self):
        return self.objectValues(['BLEntry', 'BLSubsidiaryEntry'])
    
    def manage_reverse(self, description='', effective=None, REQUEST=None):
        """
        create a reversal transaction
        """
        if self.status() != 'posted':
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Transaction not in Posted state!')
                return self.manage_main(self, REQUEST)
            return

        tid = manage_addBLSubsidiaryTransaction(self.aq_parent,
                                                title=description or 'Reversal: %s' % self.title,
                                                effective=effective or DateTime(),
                                                ref=self)
        txn = self.aq_parent._getOb(tid)

        for id,entry in self.entries():
            e = entry._getCopy(entry)
            e.amount = entry.amount * -1
            e.title = 'Reversal: %s' % entry.title
            e.ledger = ''
            txn._setObject(id, e)

        # we don't want any of these entries included in future calculations ...

        txn.manage_post()
        txn._status('postedreversal')
        
        self.setReference(txn)
	self._status('reversed')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_migrateIds(self, REQUEST=None):
        """
        old-style entries used the underlying account number, but this binds
        incorrectly
        """
        count = 0
        for k,v in self.entryItems():
            if len(k) == 7 and k[0] == 'A':
                id = self.generateId()
                self._delObject(k, suppress_events=True)
                v._setId(id)
                self._setObject(id, v)
            count += 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'migrated %i entries' % count)
            return self.manage_main(self, REQUEST)

    def Xmanage_migrateFX(self, REQUEST=None):
        """
        we're instituting a new FX scheme whereby we save any cross-currency
        amount in the entry's posted_amount attribute instead of the fx_rate
        of the past
        """
        count = 0
        if self.isMultiCurrency():
            control_currency = self.blLedger().controlAccount().base_currency
            for posted in self.postedValues():
                entry = self.entry(posted.accountId())
                if posted.amount.currency() != control_currency:
                    if not getattr(aq_base(posted), 'posted_amount', None):
                        if entry.amount.currency() == control_currency:
                            posted.posted_amount = entry.amount
                        else:
                            rate = getattr(posted, 'fx_rate', None)
                            if not rate:
                                rate = self.portal_bastionledger.crossMidRate(control_currency, 
                                                                              entry.amount.currency(), 
                                                                              self.effective_date)

                            posted.posted_amount = ZCurrency(control_currency, 
                                                             entry.amount.amount() / rate)

                if entry.amount.currency() != control_currency:
                    if not getattr(aq_base(entry), 'posted_amount', None):
                        entry.posted_amount = getattr(posted, 'posted_amount', None) or posted.amount

                count += 1
            #bad = self.manage_verify()
            #if bad:
            #    raise AssertionError, bad
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'added %i posted_amount attributes' % count)
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLSubsidiaryTransaction)
