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

import AccessControl, types, logging, transaction
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_base

from Products.BastionBanking.ZCurrency import ZCurrency
from Products.CMFCore import permissions

from utils import floor_date
from BLBase import ProductsDictionary 
from BLBase import OrderedFolder
from BLTransaction import BLTransaction
from BLEntryTemplate import BLEntryTemplate
from BLEntry import manage_addBLEntry, BLEntry
from BLSubsidiaryEntry import manage_addBLSubsidiaryEntry
from BLSubsidiaryLedger import BLSubsidiaryLedger
from Permissions import OperateBastionLedgers
from Exceptions import PostingError

LOG = logging.getLogger('BLTransactionTemplate')

manage_addBLTransactionTemplateForm = PageTemplateFile('zpt/add_transactiontmpl', globals()) 
def manage_addBLTransactionTemplate(self, id, title='', REQUEST=None):
    """
    BLTransactionTemplate factory method
    """
    assert self.this().meta_type in ['BLProcess', 'FSBLProcess'], 'Wrong container type!'

    self._setObject( id, BLTransactionTemplate(id, title) )
    
    if REQUEST is not None:
       return self.manage_main(self, REQUEST)

    return 0

class BLTransactionTemplate( OrderedFolder ):
    """
    This class provides meta-information to generate a BLTransaction.

    """
    meta_type = portal_type = 'BLTransactionTemplate'
    manage_options =  (
        { 'label':'Entries',     'action': 'manage_main'},
        { 'label':'View',        'action': '' },
        { 'label':'Test',        'action': 'manage_test' },
        ) + OrderedFolder.manage_options[2:-2]
    
    _security = ClassSecurityInfo()
    __ac_permissions__ = OrderedFolder.__ac_permissions__ + (
	(view_management_screens, ('manage_test',)),
        (OperateBastionLedgers, ('generate',)),
        )
    __replaceable__ = 1
    _manage_test = PageTemplateFile('zpt/test_transaction', globals())
    
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def generate(self, *args, **kw):
        """
        call the script - if the first arg isn't an account (or a list of accounts), then if
        it's a subsidiary ledger, pass it the ledger's Accounts, otherwise use an empty list...

        key words include effective_date, accounts
        """
        args = list(args)
        try:
            accounts = args.pop(0)
        except:
            try:
                accounts = kw['accounts']
            except:
                #ledger = self.aq_parent.aq_parent.aq_parent
                ledger = self.aq_parent
                LOG.debug('ledger=%s' % ledger)
                if isinstance(ledger, BLSubsidiaryLedger):
                    accounts = ledger.accountValues()
                else:
                    accounts = [ None ]

        LOG.debug('%s, accounts=%s, args=%s, kw=%s' % (self.getId(), str(accounts), args, kw))

        if type(accounts) != type([]):
            accounts = [ accounts ]
        #
        # hmmm - bindings (as bastardised from  Shared/DC/Scripts/Bindings.py)
        #
        container = self.aq_inner.aq_parent      # this is us (kind of round-about way to discover it ...)
        context = self.aq_parent                 # this could be our BLAccount derivation ...

        # a BLTransactionTemplate can only appear in a ledger/Processes folder so ...
        #ledger = container.aq_parent.aq_parent
        ledger = self.aq_parent

        #raise AssertionError, (container, context, ledger, self, accounts)
        LOG.debug( "%s %s %s %s, %s, %s)" %  (container.getId(), ledger.getId(), self.getId(), accounts, args, kw))
        # we want to put the txn in the 'ledger', but the entry in the 'account' ie the context ...
        transaction = ledger.createTransaction(title='Auto - %s' % self.getId(),
                                               effective=kw.get('effective', DateTime(ledger.timezone)))
        for prop in transaction.propertyIds():
            if kw.has_key(prop):
                transaction._updateProperty(prop, kw[prop])

        templates = filter(lambda x: isinstance(x, BLEntryTemplate), self.objectValues())

        # TODO - this f**ks up ordered folder entry priorities ... we need to move this into
        # FS Directory views perhaps ...
        templates.sort()

        LOG.debug("templates=%s" % templates)
        # we need to take into account all sorts of funky inheritance like for FSEntryTemplate ...
        for entry_template in templates:
            # account is probably only an attribute of a BLEntryTemplate ...
            if getattr(aq_base(entry_template), 'account', None):
                try:
                    account = entry_template.blAccount()
                except:
                    raise KeyError, "%s (%s)" % (entry_template.getId(), entry_template.account)
                entries = entry_template.__of__(transaction).generate(account=account, args=args,kw=kw)
            else:
                entries = []
                for account in accounts:
                    entries.extend(entry_template.__of__(transaction).generate(account=account,args=args,kw=kw))

            if not type(entries) in ( types.ListType, types.TupleType ):
                raise SyntaxError, "BLEntryTemplate must return a list: %s" % entry_template_id

            LOG.debug("%s returns %s" %  (entry_template.getId(), entries))

            for entry in entries:

                if not isinstance(entry, BLEntry):
                    raise SyntaxError, "Non-BLEntry derivative (got a %s - %s)!!" % (entry.meta_type, entry)

                # drop zero-value entries
                if entry.amount == 0:
                    continue

                # do aggregation (overridden in transaction._setObject)
		id = transaction.generateId()
		entry.id = id
                transaction._setObject(id, entry)

        if transaction.status() != 'complete':
           raise PostingError,"Does not balance %s != %s [%s]!\n%s" % (transaction.debitTotal(),
                                                                       transaction.creditTotal(),
                                                                       transaction.status(),
                                                                       str(transaction))
        try:
            transaction.manage_statusModify(workflow_action='post')
        except:
            LOG.error(transaction)
            raise

        return transaction

    def manage_test(self, REQUEST):
        """ show what the txn template would do - and rollback ..."""
        try:
            REQUEST.set('manage_tabs_message', 'This template would generate and post the following transaction...')
            return self._manage_test(self, REQUEST)
        finally:
            transaction.get().abort()

    def all_meta_types(self):
        return ( ProductsDictionary('BLEntryTemplate'),
                 ProductsDictionary('Script (Python)'),)
    
    def ZPythonScript_editAction(self, REQUEST, title, params, body):
        """ """
        PythonScript.ZPythonScript_editAction(self, REQUEST, title, self._params, body)

    def ZPythonScript_edit(self, params, body):
        PythonScript.ZPythonScript_edit(self, self._params, body)

AccessControl.class_init.InitializeClass(BLTransactionTemplate)
