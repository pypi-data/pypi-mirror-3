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

import AccessControl, string, copy, operator, types, logging
from Acquisition import aq_base, aq_parent
from AccessControl.Permissions import view_management_screens, access_contents_information
from DateTime import DateTime
from Acquisition import aq_base, aq_inner, aq_self
from OFS.ObjectManager import BeforeDeleteException
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.publisher.interfaces import IPublishTraverse

from BLBase import *
from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES

from interfaces.ledger import ILedger, IBLLedger
from BLAccount import BLAccount, BLAccounts
from BLTransaction import BLTransaction, BLTransactions, manage_addBLTransaction
from BLEntry import BLEntry
from BLProcess import BLProcess
from BLReport import BLReportFolder
from Exceptions import MissingAssociation
from Permissions import ManageBastionLedgers, OperateBastionLedgers
from Products.CMFCore import permissions

from SyndicationSupport import SyndicationSupport, SYNDICATION_ACTION

MARKER = []
LOG = logging.getLogger('BLLedger')

def assoc_cmp(x,y):
    t1 = x['tag']
    t2 = y['tag']
    if t1 < t2: return -1
    if t1 > t2: return 1
    return 0

manage_addBLLedgerForm = PageTemplateFile('zpt/add_blledger', globals())
def manage_addBLLedger(self, id, title, currencies, REQUEST=None):
    """ a double entry ledger - you shouldn't be able to directly create one of these ... """

    try:
        self._setObject(id, BLLedger(id, title, currencies))
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class LedgerBase(BObjectManagerTree, BSimpleItem):
    """
    A ledger.  The common sheet is to define extension fields to all account objects.

    """
    implements(ILedger, IPublishTraverse)

    default_page = 'blchart_view'
    Types = [ 'Asset', 'Liability', 'Proprietorship', 'Income', 'Expense' ]

    account_types = ('BLAccount',)
    transaction_types = ('BLTransaction',)

    _properties = BObjectManagerTree._properties + (
        {'id':'currencies',         'type':'lines',     'mode':'w'},
        {'id':'account_prefix',     'type':'string',    'mode':'w'},
        {'id':'txn_prefix',         'type':'string',    'mode':'w'},
        {'id':'email',              'type':'string',    'mode':'w'},
        {'id':'account_types',      'type':'lines',     'mode':'r'}, 
        {'id':'transaction_types',  'type':'lines',     'mode':'r'}, 
        )

    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (OperateBastionLedgers, ('createTransaction', 'manage_reverse',
                                 'manage_post', 'manage_cancel', 'manage_postTransactions',
                                 'nextAccountId', 'nextTxnId')),
        (ManageBastionLedgers, ('manage_edit', 'manage_delTags', 'manage_addTag',
                                'manage_renameTags', 'manage_repost') ),
        (view_management_screens, ('manage_accounts', 'manage_transactions',
                                   'manage_processes', 'manage_Reports',) ),
        (access_contents_information, ('accountValues', 'accountIds', 'subtypes',
                                       'sum', 'debitTotal', 'creditTotal', 'total',
                                       'asCSV', 'searchObjects', 'totals',
                                       'saveSearch', 'syndicationQuery',
                                       'manage_downloadCSV', 'associations',
                                       'accountsForTag', 'zeroAmount',
                                       'lastTransaction', 'firstTransaction',
                                       'transactionValues', 'transactionIds', 'defaultCurrency',
                                       'entryValues', 'allCurrencies', 'accountId', 'txnId',
                                       'emailAddress')),
        ) + BSimpleItem.__ac_permissions__

    #dontAllowCopyAndPaste=0
    #__allow_access_to_unprotected_subobjects__ = 1

    manage_options = (
        #{'label': 'Extensions',   'action': 'manage_common_sheet',
        #             'help':('BastionLedger', 'account_attrs.stx')},
        {'label': 'Accounts',     'action': 'manage_accounts' },
        {'label': 'View',         'action': '' },
        {'label': 'Associations', 'action': 'manage_associations' },
        {'label': 'Transactions', 'action': 'manage_transactions' },
        {'label': 'Properties',   'action': 'manage_propertiesForm',
         'help':('BastionLedger', 'ledger.stx') },
        {'label': 'Reports',      'action': 'manage_Reports' },
        {'label': 'Processes',    'action': 'manage_processes' },
    ) + BSimpleItem.manage_options

    manage_propertiesForm = PageTemplateFile('zpt/edit_ledger', globals())
    manage_associations = PageTemplateFile('zpt/associations', globals())
    manage_accounts = PageTemplateFile('zpt/view_chart', globals())
    manage_main = PageTemplateFile('zpt/view_chart', globals())
    manage_transactions = PageTemplateFile('zpt/view_transactions', globals())
    manage_processes = PageTemplateFile('zpt/processes', globals())
    
    manage_btree = BObjectManagerTree.manage_main
    manage_zpropertiesForm = BObjectManagerTree.manage_propertiesForm

    #def manage_Processes(self, REQUEST):
    #    """ """
    #    REQUEST.RESPONSE.redirect('Processes/manage_main')

    def manage_Reports(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('Reports/manage_main')

    def __init__(self, id, title, currencies, account_id=1, account_prefix='A',
                 txn_id=1, txn_prefix='T'):
        BObjectManagerTree.__init__(self, id)
        self.Accounts = BLAccounts('Accounts', '',)  # index for accounts
        self.Transactions = BLTransactions('Transactions', '')    # index for transactions
        self.Reports = BLReportFolder('Reports','')
        LedgerBase.manage_edit(self, title, title,  txn_id, account_id, account_prefix, txn_prefix, currencies)
        cat = self.catalog = ZCatalog('catalog')        
        cat.addIndex('id', 'FieldIndex')
        cat.addIndex('meta_type', 'FieldIndex')
        try:
            cat.addIndex('title', 'TextIndexNG3')
        except:
            cat.addIndex('title', 'FieldIndex')
        cat.addIndex('date', 'FieldIndex')
        cat.addIndex('type', 'FieldIndex')
        cat.addIndex('account', 'FieldIndex')
        cat.addIndex('transaction', 'FieldIndex')

        # Adding metadata columns
        for name in ('id', 'meta_type', 'title', 'date', 'account', 'transaction', 'accno'):
            try:
                cat.addColumn(name)
            except:
                raise

    def displayContentsTab(self):
        """ 
        we don't allow copy/paste/delete etc
        """
        return False


    def Xmanage_afterClone(self, item):
        # recatalog the Accounts ...
        accounts = self.Accounts
        accounts.manage_catalogClear()
        path = '/'.join(accounts.getPhysicalPath())
        accounts.ZopeFindAndApply(self,
                                  obj_metatypes=self.account_types,
                                  obj_ids=None,
                                  obj_searchterm=None,
                                  obj_expr=None,
                                  obj_mtime=None,
                                  obj_mspec=None,
                                  obj_permission=None,
                                  obj_roles=None,
                                  search_sub=0,
                                  REQUEST={},
                                  apply_func=accounts.catalog_object,
                                  apply_path=path)

    def createTransaction(self, effective=None, title='',entries=[]):
        """
        return a newly created BLTransaction
        """
        txn_id = manage_addBLTransaction(self, 
                                         title=title, 
                                         effective=effective or DateTime(), 
                                         entries=entries)
        return self._getOb(txn_id)

    def manage_edit(self, title, description, txn_id, account_id, account_prefix,
                    txn_prefix, currencies, email='', REQUEST=None):
        """
        """
        self.title = title
        self.description = description
        self.currencies = currencies
        self.account_prefix = account_prefix
        self.txn_prefix = txn_prefix
        self._next_txn_id = int(txn_id)
        self._next_account_id = int(account_id)
        self.email = email
        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', 'Updated')
            REQUEST.set('management_view', 'Properties')
            return self.manage_propertiesForm(self, REQUEST)

    #
    # WARNING!!!
    #
    # we *cannot* create a __getattr__ and *still* use getToolByName
    # to find our portal_bastionledger - death by (silent) recursion
    # failure ...
    #
    def publishTraverse(self, REQUEST, name):
        """
        if we can't find the object - go see if it's a BLProcess and then dispatch
        it ala this ledger
        """
        LOG.debug('publishTraverse(%s)' % name)
        # 'manage_interfaces' drops off because it's implemented as a Five browser view
        if name == 'manage_interfaces':
            return BObjectManagerTree.publishTraverse(self, REQUEST, name)
        return getattr(self, name, None) or self._getProcess(name)

    __bobo_traverse__ = publishTraverse

    def _getProcess(self, name):
        """
        go see if the name is a process, and if so, return it in our acquisition context
        """
        if not name.startswith('_'):
            LOG.debug('_getProcess(%s)' % name)
            tool = getToolByName(aq_parent(self), 'portal_bastionledger')
            try:             
                obj = tool._getOb(name)
                if isinstance(obj, BLProcess):
                    return aq_base(obj).__of__(self)
            except (AttributeError, KeyError):
                pass
        return None

    def all_meta_types(self):
        """
        this is needed to identify pasteable types (for non-visibles ...)
        """
        return filter(lambda x: x,
                      map(lambda x: ProductsDictionary(x),
                          self.account_types + self.transaction_types)) 

    def accountValues(self, REQUEST=None, **kw):
        """
        return all the accounts - if you pass kw, it does a catalog search
        """
        if kw:
            return self.Accounts(REQUEST=REQUEST, **kw)
        return self.objectValues(self.account_types)

    def transactionValues(self, REQUEST={}, **kw):
        """
        return all the transactions - if you pass kw, it does a catalog search
        """
        if kw or REQUEST:
            query = {}
            if REQUEST:
                query.update(REQUEST.form)
            # overwrite any form parameters ...
            if kw:
                query.update(kw)

            from_date = to_date = None
            if query.has_key('from_date') and not query.has_key('effective_date'):
                try:
                    from_date = DateTime(query['from_date'])
                except:
                    pass
            if query.has_key('to_date') and not query.has_key('effective_date'):
                try:
                    to_date = DateTime(query['to_date'])
                except:
                    pass

            if from_date and to_date:
                query['effective_date'] = (from_date, to_date)
                query['effective_date_usage'] = 'range:min:max'
            elif from_date:
                query['effective_date'] = from_date
                query['effective_date_usage'] = 'range:max'
            elif to_date:
                query['effective_date'] = to_date
                query['effective_date_usage'] = 'range:min'

            LOG.info('Querying Transactions: %s' % str(query))
            results = self.Transactions(**query)
            if query.has_key('title') and query['title']:
                if query.has_key('case_sensitive'):
                    return filter(lambda x: x.title.find(query['title']) != -1, results)
                else:
                    ltitle = query['title'].lower()
                    return filter(lambda x: x.title.lower().find(ltitle) != -1, results)
            return results
        return self.objectValues(self.transaction_types)

    def entryValues(self, REQUEST={}, **kw):
        """
        return all the entries - if you pass kw, it does a catalog search,
        sort order is as per txn sorting
        """
        results = []
        for txn in self.transactionValues(REQUEST, **kw):
            results.extend(txn.entryValues())
        return results

    def accountIds(self):
        return self.objectIds(self.account_types)

    def transactionIds(self):
        return self.objectIds(self.transaction_types)
    
    def uniqueTransactionValues(self, ndx):
        return self.Transactions.uniqueValuesFor(ndx)

    def lastTransaction(self):
        """
        return the last transaction (by date) in a ledger
        """
        brainz = self.Transactions.searchResults(sort_on='effective_date',
                                                 sort_order='descending')
        if brainz:
            return brainz[0].getObject()

        return None

    def firstTransaction(self):
        """
        return the first transaction (by date) in a ledger
        """
        brainz = self.Transactions.searchResults(sort_on='effective_date',
                                                 sort_order='ascending')
        if brainz:
            return brainz[0].getObject()

        return None

    def nextTxnId(self):
        id = str(self._next_txn_id)
        self._next_txn_id += 1
        return "%s%s" % (self.txn_prefix, string.zfill(id, 12))

    def nextAccountId(self):
        id = str(self._next_account_id)
        self._next_account_id += 1
        return "%s%s" % (self.account_prefix, string.zfill(id, 6))

    def _resetNextAccountId(self, value):
        """ hmmm - if you really *must* tweak our private data """
        self._next_account_id = value

    def generateUniqueId(self, type=None):
        """
        ham it up for Plone's createObject and portal_factory
        """
        if type.find('Transaction') != -1:
            return self.nextTxnId()
        elif type.find('Account') != -1 or type in ('BLShareholder', 'BLEmployee'):
            return self.nextAccountId()
        else:
            # ok we want to call the plone skin and have to throw it up past all this
            # BL stuff ....
            return getToolByName(self, 'portal_url').generateUniqueId(type)

    def defaultCurrency(self):
        """ either the first currency in the list, or the Ledger's """
        if len(self.currencies) > 0:
            return self.currencies[0]
        return self.aq_parent.currency
    
    def allCurrencies(self):
	""" list acceptable currencies (with the ledger default first in list)"""
        currencies = list(self.portal_bastionledger.Currencies())
        default = self.aq_parent.currency
        # hmmm - hackery in case our parent isn't really a Ledger ;)
        if callable(default):
            default = default()
        try:
            currencies.remove(default)
        except:
            pass
        return [ default ] + currencies

    def _delObject(self, id, tp=1, suppress_events=False):
        ob = self._getOb(id)
        if not self.expertMode() and issubclass(ob.__class__, BLAccount) and not ob.balance() == 0:
            raise BeforeDeleteException, 'Account(%s) has a balance!' % ob.getId()
        BObjectManagerTree._delObject(self, id, tp, suppress_events=suppress_events)

    def accountId(self):
        return self._next_account_id

    def txnId(self):
        return self._next_txn_id

    def manage_postTransactions(self, ids=[], REQUEST=None):
        """
        """
        map ( lambda x, y=self: y._getOb(x).content_status_modify(workflow_action='post'), ids )
        if REQUEST is not None:
            return self.manage_transactions(self, REQUEST)
    

    #
    # reroute these guys (from OFS.CopySupport) ....
    #
    def manage_cutObjects(self, ids=None, REQUEST=None):
        """Put a reference to the objects named in ids in the clip board"""
        cp = BObjectManagerTree.manage_cutObjects(self, ids)
        if REQUEST is not None:
            resp=REQUEST['RESPONSE']
            resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
            REQUEST['__cp'] = cp
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return cp

    def manage_copyObjects(self, ids=None, REQUEST=None, RESPONSE=None):
        """Put a reference to the objects named in ids in the clip board"""
        cp = BObjectManagerTree.manage_copyObjects(self, ids)
        if REQUEST is not None:
            resp=REQUEST['RESPONSE']
            resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
            REQUEST['__cp'] = cp
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return cp
    
    def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
        """Paste previously copied objects into the current object.
           If calling manage_pasteObjects from python code, pass
           the result of a previous call to manage_cutObjects or
           manage_copyObjects as the first argument."""
        if cb_copy_data is not None:
            cp=cb_copy_data
        else:
            if REQUEST and REQUEST.has_key('__cp'):
                cp=REQUEST['__cp']
        try:
            result = BObjectManagerTree.manage_pasteObjects(self, cp)
        except:
            raise
        
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))
        return result
    
    def manage_renameObjects(self, ids=[], new_ids=[], REQUEST=None):
        """Rename several sub-objects"""
        BObjectManagerTree.manage_renameObjects(self, ids, new_ids)
        #
        # hmmm - there is no dispatch_to here because we'd have to edit the rename form ...
        #
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))


    def manage_renameObject(self, id, new_id, REQUEST=None):
        """Rename a particular sub-object"""
        BObjectManagerTree.manage_renameObject(self, id, new_id)
        #
        # hmmm - there is no dispatch_to here because we'd have to edit the rename form ...
        #
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/%s' % (REQUEST['URL1'], REQUEST.get('dispatch_to', 'manage_main')))


    def emailAddress(self):
        """
        return email address
        """
        email = self.email
        if email.find('<') != -1:
            return email
        return '"%s" <%s>' % (self.getId(), email)

    def __str__(self):
        return "<%s instance %s at %s)>" % (self.meta_type,
                                            self.getId(),
                                            self.absolute_url())

    __repr__ = __str__


    def _reset(self):
        """ remove all account/txn entries only (ie no other stuff!!) """
        for account in self.accountValues():
            for (id, e) in filter(lambda (x,y): isinstance(y, BLEntry), account.objectItems()):
                account._delObject(id, suppress_events=True, force=True)
        self.Accounts.refreshCatalog()
        for id in self.objectIds(self.transaction_types):
            self._delOb(id)
        self.Transactions.manage_catalogClear()
        self._next_txn_id = 1

    def manage_delObjects(self, ids=[], REQUEST=None):
        """
        """
        if ids:
            BObjectManagerTree.manage_delObjects(self, ids)

        # dispatch get's f**ked up - need to identify what came from txn view ...
        if REQUEST:
            if REQUEST.get('sort_on','') == 'effective_date':
                return self.manage_transactions(self, REQUEST)

            return self.manage_main(self, REQUEST)

    def manage_delTags(self, ids, REQUEST=None):
        """
        Remove tags from underlying accounts
        """
        # we're only blitzing local tags :)
        for account in self.Accounts(tags=ids):
            tags = list(account.tags)
            for tag in ids:
                if tag in tags:
                    tags.remove(tag)
            account.updateTags('tags', tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            REQUEST.set('manage_tabs_message', 'Deleted %s' % ', '.join(ids))
            return self.manage_associations(self, REQUEST)

    def manage_addTag(self, tag, accnos=[], REQUEST=None):
        """
        add the tag to the specified list of account ids
        """
        assoc = getToolByName(self, 'portal_bastionledger').associations.get(tag)

        if not assoc and accnos:
            catalog = self.Accounts
            for account in catalog(accno=accnos):
                tags = list(account.tags)
                if not tag in tags:
                    tags.append(tag)
                    account.updateTags(tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            return self.manage_associations(self, REQUEST)

    def manage_renameTags(self, ids, tag, REQUEST=None):
        """
        rename tags in underlying accounts
        """
        catalog = self.Accounts
        for id in ids:
            for account in catalog(tags=id):
                tags = list(account.tags)
                tags.remove(id)
                tags.append(tag)
                account.updateTags(tags)
        if REQUEST:
            REQUEST.set('management_view', 'Associations')
            return self.manage_associations(self, REQUEST)

    def associations(self):
        """
        return a hash of local and global associations (tags)
        """
        results = {}
        bltool = getToolByName(self, 'portal_bastionledger', None)
        if bltool:
            associations = getattr(bltool, 'associations', None)
            if associations:
                for assoc in map(lambda x: {'tag':x.getId(),
                                            'accno': list(x.accno),
                                            'global':True},
                                 associations.searchObjects(ledger=self.getId())):
                    results[assoc['tag']] = assoc
        # f**k knows why we get None in this ...
        for tag in filter(lambda x:x,self.Accounts.uniqueValuesFor('tags')):
            if results.has_key(tag):
                accnos = results[tag]['accno']
                for accno in map(lambda x:x.accno, self.Accounts(tags=tag)):
                    if accno not in accnos:
                        accnos.append(accno)
            else:
                results[tag] = {'tag': tag,
                                'accno': map(lambda x:x.accno,
                                             self.Accounts(tags=tag)),
                                'global':False}
        results = results.values()
        results.sort(assoc_cmp)
        return results

    def accountsForTag(self, tag, optional=False):
        """
        show all the accounts that are associated by the tag name

        setting optional allows you to return an empty list if the tag isn't expected
        to return accounts
        """
        # we've reimplemented Accounts searching ...
        accounts = self.accountValues(tags=tag)
        if not accounts and not optional:
            raise MissingAssociation, tag
        return accounts

    def subtypes(self, type=''):
        if type:
            stypes = map( lambda x: x.subtype, self.Accounts(type=type) )
            ret = []
            for stype in stypes:
                if stype == '':
                    continue
                if ret.count(stype) == 0:
                    ret.append(stype)
            return ret
        else:
            return self.uniqueValuesFor('subtype')

    def sum(self, effective=None, tags=[], REQUEST={}, *args, **kw):
        """
        perform an account balance summation of the given ZCatalog query
        """
        if REQUEST:
            criteria = REQUEST
        else:
            criteria = kw

        if tags:
            if type(tags) not in (types.ListType, types.TupleType):
                tags = [tags]
            seen = {}
            for t in tags:
                try:
                    for account in self.accountsForTag(t):
                        seen[account.accno] = 1
                except MissingAssociation:
                    pass
            if seen:
                if criteria.has_key('accno'):
                    criteria['accno'].extend(seen.keys())
                else:
                    criteria['accno'] = seen.keys()

        criteria['meta_type'] = self.account_types

        currency = self.defaultCurrency()

        if effective:
            if type(effective) not in (types.TupleType, types.ListType):
                effective = (EPOCH, effective)
            balances = map(lambda x:x.total(effective=effective, currency=currency),
                           self.Accounts(criteria))
        else:
            balances = map(lambda x:x.total(currency=currency), self.Accounts(criteria))
        if balances:
            return reduce(operator.add, balances)
        return ZCurrency(currency, 0)

    def debitTotal(self, effective=None, *args, **kw):
        """
        return the debit side of the query
        """
        if effective:
            balances = map( lambda x:x.debitTotal(effective=effective),
                            self.Accounts(kw) )
        else:
            balances = map( lambda x:x.debitTotal(), self.Accounts(kw) )
        if balances:
            return reduce(operator.add, balances )
        return ZCurrency(self.defaultCurrency(), 0)

    def creditTotal(self, effective=None, *args, **kw):
        """
        return the credit side of the query
        """
        if effective:
            balances = map( lambda x:x.creditTotal(effective=effective),
                            self.Accounts(kw) )
        else:
            balances = map( lambda x:x.creditTotal(), self.Accounts(kw) )
        if balances:
            return reduce(operator.add, balances )
        return ZCurrency(self.defaultCurrency(), 0)

    def total(self, currency=None, effective=None):
        """
        calculate the value of the ledger
        """
        # hmmm subsidiary ledger's could be multi-currency which would require fx conversions
        # on balances, but this has already been done for the control account within the
        # txn posting process, so not only don't we have to sum, we don't have to convert...
        #if getattr(aq_base(self.aq_parent), 'controlEntry', None):
        #    return self.aq_parent.controlEntry().amount
        if not currency:
            currency = self.defaultCurrency()

        amount = ZCurrency(currency, 0)

        for account in self.accountValues():
            amount += account.total(currency=currency, effective=effective)

        return amount

    def saveSearch(self, request):
        """
        Our canned txn query
        """
        request.set('entered_by', request.get('entered_by', ''))
        request.set('status', request.get('status', ''))
        request.set('effective_start', request.get('effective_start', DateTime() - 1))
        request.set('effective_end', request.get('effective_end', DateTime()))
        request.set('batchsize', request.get('batchsize', 20))
        request.set('sort_on', 'effective_date')
        request.set('sort_order', 'descending')
        request.SESSION['txns'] = request.form

    def manage_reverse(self, ids=[], REQUEST=None):
        """ generate and apply reversal entries """
        for id in ids:
            self._getOb(id).manage_reverse()
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def manage_post(self, ids=[], REQUEST=None):
        """
        set Unposted transaction(s) status to posted
        """
        for id in ids:
            txn = self._getOb(id)
            txn.manage_post()

        if REQUEST:
            return self.manage_transactions(self, REQUEST)
            
    def manage_cancel(self, ids=[], REQUEST=None):
        """
        set Unposted transaction(s) status to cancelled
        """
        for id in ids:
            txn =self._getOb(id)
            if txn.status() == 'posted':
                txn.manage_reverse()
	    elif txn.status() in ('incomplete', 'complete'):
		txn.manage_cancel()
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def manage_repost(self, ids=[], REQUEST=None):
        """
        hmmm - repost transactions - shouldn't be necessary, but useful
        if copy/pasting between ledger instances and may form part of a
        future 'playback' feature
        """
        for id in ids:
            txn = self._getOb(id)
            txn.manage_repost()

        if REQUEST:
            return self.manage_transactions(self, REQUEST)


    def manage_fixupTransactionEntries(self, REQUEST=None):
        """
        """
        for txn in self.transactionValues():
            for entry in txn.entryValues():
                if entry.account.find('Accounts/') != -1:
                    entry.account = entry.account.replace('Accounts/', '')
                if not entry.ledger:
                    entry.ledger = entry.account.split('/')[0]
        if REQUEST:
            return self.manage_transactions(self, REQUEST)

    def migrateAccountsTransactions(self, REQUEST=None):
        """
        a big reorg to take account and transaction objects and stuff them directly
        into the ledger, whilst still leaving their catalog infrastructure

        this is necessitated because of the way we create objects in Plone ...
        """
        # Zope find support only finds stuff in containment relationships ...
        self.Accounts.manage_catalogClear()

        while self.Accounts.objectValues():
            for account in self.Accounts.objectValues():
                for entry in account.entryValues():
                    if entry.account.find('Accounts/') != -1:
                        entry.account = entry.account.replace('Accounts/', '')
                    # seems control entries don't have ledger set - there's no reason why not ...
                    if entry.isControlEntry():
                        entry.ledger = entry.getId()
                    #entry.reindexObject()
                self.Accounts._delOb(account.getId())
                self._setObject(account.getId(), account)

        self.Accounts.manage_catalogFoundItems()
        self.Transactions.manage_catalogClear()

        while self.Transactions.objectValues():
            for txn in self.Transactions.objectValues():
                self.Transactions._delOb(txn.getId())
                self._setObject(txn.getId(), txn)
                # hmmm - they all seem to be incomplete
                txn = self._getOb(txn.getId())
                for entry in txn.entryValues():
                    if entry.account.find('Accounts/') != -1:
                        entry.account = entry.account.replace('Accounts/', '')
                    if not entry.ledger:
                        entry.ledger = entry.account.split('/')[0]
                txn.setStatus()

        self.Transactions.manage_catalogFoundItems()

        if getattr(aq_base(self), 'Reports', None):
            delattr(self, 'Reports')
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Migrated')
            return self.manage_main(self, REQUEST)

    def zeroAmount(self):
        """
        return a zero amount in the default currency of the ledger
        """
        return ZCurrency('%s 0.00' % self.defaultCurrency())

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%0.2f', txns=True, REQUEST=None):
        """
        comma-separated transaction/account entries

        the default currency representation is float - use %a (or something with %c) for
        currency code inclusion
        """
        if txns:
            return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt),
                                 self.transactionValues()))
        else:
            return '\n'.join(map(lambda x: x.asCSV(datefmt, curfmt),
                                 self.accountValues()))

    def manage_downloadCSV(self, REQUEST, RESPONSE, datefmt='%Y/%m/%d', curfmt='%0.2f', txns=True):
        """
        comma-separated transaction/account entries

        the default currency representation is float - use %a (or something with %c) for
        currency code inclusion
        """
        RESPONSE.setHeader('Content-Type', 'application/octetstream')
        RESPONSE.setHeader('Content-Disposition',
                           'inline; filename=%s.csv' % self.getId().lower())
        RESPONSE.write(self.asCSV(datefmt, curfmt, txns))

    #
    # Syndication Stuff
    # 
    def searchObjects(self, **kw):
        """
        """
        return self.Accounts.searchObjects(**kw)

    def syndicationQuery(self):
        """
        """
        return {'meta_type':self.account_types,
                'CreationDate':{'query':DateTime() - 1,
                                'range':'min'}}

    def _postCopy(self, container, op=0):
        # Called after the copy is finished to accomodate special cases.
        # The op var is 0 for a copy, 1 for a move.
        path = '/'.join(self.getPhysicalPath())

        accounts = self.Accounts
        accounts.manage_catalogClear()
        accounts.ZopeFindAndApply(self,
                                  obj_metatypes=self.account_types,
                                  obj_ids=None,
                                  obj_searchterm=None,
                                  obj_expr=None,
                                  obj_mtime=None,
                                  obj_mspec=None,
                                  obj_permission=None,
                                  obj_roles=None,
                                  search_sub=0,
                                  REQUEST={},
                                  apply_func=accounts.catalog_object,
                                  apply_path=path)

        transactions = self.Transactions
        transactions.manage_catalogClear()
        transactions.ZopeFindAndApply(self,
                                      obj_metatypes=self.transaction_types,
                                      obj_ids=None,
                                      obj_searchterm=None,
                                      obj_expr=None,
                                      obj_mtime=None,
                                      obj_mspec=None,
                                      obj_permission=None,
                                      obj_roles=None,
                                      search_sub=0,
                                      REQUEST={},
                                      apply_func=transactions.catalog_object,
                                      apply_path=path)

    def totals(self, dates, format=None):
        """
        return balance information for a date range
        if supplied, format should be a currency format eg ('%0.2f')
        """
        if format:
            return map(lambda x: self.total(effective=x).strfcur(format), dates)
        return map(lambda x: self.total(effective=x), dates)

    def _repair(self):
        if not getattr(aq_base(self), 'Transactions', None):
            self.Transactions = BLTransactions('Transactions', '')

        if getattr(aq_base(self), 'Processes', None):
            try:
                delattr(self, 'Processes')
            except:
                pass
        for fn in (self.accountValues, self.transactionValues):
            for entry in fn():
                entry._repair()
        self.Accounts._repair()  # ensure indexes for chart views
        for txn in self.transactionValues():
            try:
                txn.setStatus()
            except:
                pass
        if not getattr(aq_base(self),'Reports', None):
            self.Reports = BLReportFolder('Reports')



class BLLedger(LedgerBase):
    """
    A ledger.  The common sheet is to define extension fields to all account objects.

    """
    meta_type = portal_type = 'BLLedger'

    implements(IBLLedger)

AccessControl.class_init.InitializeClass(BLLedger)


def cookie_path(request):
    # Return a "path" value for use in a cookie that refers
    # to the root of the Zope object space.
    return request['BASEPATH1'] or "/"

def accno_field_cmp(x, y):
    if x.accno == y.accno: return 0
    if x.accno > y.accno: return 1
    return -1

