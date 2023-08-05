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

import AccessControl, types, operator, string, sys, traceback
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens, change_permissions, \
     access_contents_information
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from DocumentTemplate.DT_Util import html_quote
from ExtensionClass import Base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.BastionBanking.ZCurrency import ZCurrency
from OFS.ObjectManager import BeforeDeleteException
from zope.interface import implements

from BLBase import *
from utils import assert_currency, floor_date, ceiling_date
from BLAttachmentSupport import BLAttachmentSupport
from Permissions import OperateBastionLedgers, OverseeBastionLedgers, ManageBastionLedgers
from Exceptions import PostingError, UnpostedError, IncorrectAmountError, InvalidTransition, UnbalancedError
from interfaces.transaction import ITransaction
import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

LOG = logging.getLogger('BLTransaction')

manage_addBLTransactionForm = PageTemplateFile('zpt/add_transaction', globals()) 
def manage_addBLTransaction(self, id='', title='',effective=None,
                            ref=None, entries=[], REQUEST=None):
    """ add a transaction """
    if ref:
        try:
            ref = '/'.join(ref.getPhysicalPath())
        except:
            pass

    if not id:
        id = self.nextTxnId()

    effective = effective or DateTime()
    if type(effective) == types.StringType:
        effective = DateTime(effective)
    effective.toZone(self.timezone)

    self._setObject(id, BLTransaction(id, title, effective, ref))

    txn = self._getOb(id)

    # don't do entries with blank amounts ...
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        try:
            assert_currency(entry.amount)
        except:
            entry.amount = ZCurrency(entry.amount)
        if entry.get('credit', False):
            entry.amount = -abs(entry.amount)
        try:
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)
        except NameError:
            # doh - more cyclic dependencies ...
            from BLEntry import manage_addBLEntry
            manage_addBLEntry(txn, entry.account, entry.amount, entry.title)

    # figure out the sorry (or otherwise) state of the transaction
    txn.setStatus()
    
    LOG.debug('created transaction: %s' % id)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % txn.absolute_url())

    return id


def addBLTransaction(self, id, title=''):
    """
    Plone constructor - we generated this id via our own generateUniqueId function
    in BLLedger ...
    """
    id = manage_addBLTransaction(self, id=id, title=title)
    return id

class BLTransaction(BObjectManagerTree, BLAttachmentSupport):

    meta_type = portal_type = 'BLTransaction'

    implements(ITransaction)
    
    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (view_management_screens, ('manage_verify',)),
        (access_contents_information, ('isMultiCurrency', 'faceCurrencies', 'postedCurrencies', 'currencies', 'effective')),
        (OperateBastionLedgers, ('manage_post', 'manage_editProperties', 'manage_toggle', 'createEntry',
                                 'manage_propertiesForm', 'setStatus', 'addEntries', 'editProperties',
				 'manage_statusModify',)),
        (OverseeBastionLedgers, ('manage_reverse','manage_cancel', 'manage_repost', 'manage_unpost')),
	(view, ('referenceUrl', 'referenceId', 'dateStr', 'blLedger', 'debitTotal',
		'creditTotal', 'total', 'modificationTime',
		'entries', 'entry', 'entryItems', 'entryValues', 'postedValues', 'modifiable')),
       ) + BLAttachmentSupport.__ac_permissions__

    _v_already_looking = 0
    
    manage_options = (
        { 'label': 'Entries',    'action' : 'manage_main',
          'help':('BastionLedger', 'transaction.stx') },
        { 'label': 'View',       'action' : '',},
        BLAttachmentSupport.manage_options[0],
        { 'label': 'Verify',       'action' : 'manage_verify',},
        { 'label': 'Properties', 'action' : 'manage_propertiesForm'},
        ) + BSimpleItem.manage_options

    manage_main = PageTemplateFile('zpt/view_transaction', globals())

    #manage_main = BObjectManagerTree.manage_main
    default_page = 'bltransaction_view'

    _properties = ( 
        {'id':'title',          'type':'string',    'mode':'w' },
        {'id':'effective_date', 'type':'date',      'mode':'w' },
        {'id':'entered_by',     'type':'string',    'mode':'r' },
        {'id':'entered_date',   'type':'date',      'mode':'r' },
        {'id':'reference',      'type':'string',    'mode':'w' },
        )
    
    def __init__(self, id, title='', date=None, reference=None):
        BObjectManagerTree.__init__(self, id)
        self.title = title
        self.effective_date = floor_date(date or DateTime())
        self.entered_by = getSecurityManager().getUser().getUserName()
        self.entered_date = DateTime()
        self.reference = reference

    def catalog(self):
        return self.aq_parent.Transactions


    #
    # a reference may or may not be a reference to an object on the system ...
    #
    def referenceObject(self):
        """
        return the object that's referenced to this transaction
        """
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference)
            except:
                pass
        return None
            
    def referenceUrl(self):
        if self.reference:
            try:
                return self.unrestrictedTraverse(self.reference).absolute_url()
            except:
                pass
        return None

    def referenceId(self):
        return string.split(self.reference, '/').pop()

    def effective(self):
        """ the effective date of the transaction - expressed as the earliest time for the ledger timezone """
        return floor_date(self.effective_date) # toZone(self.timezone)

    def dateStr(self): return self.day.strftime('%Y-%m-%d %H:%M:%S')

    def blLedger(self):
        #
        # Transactions are buried within the 'Transactions' folder of a Ledger ...
        #
        return self.aq_parent
    
    def all_meta_types(self):
        """ """
        return [ ProductsDictionary('BLEntry') ]

    def filtered_meta_types(self, request=None):
        """ """
        if self.status() in ['incomplete', 'complete']:
            return [ ProductsDictionary('BLEntry') ]
        return []

    def defaultCurrency(self):
        """
        """
        return self.aq_parent.defaultCurrency()

    def isMultiCurrency(self):
        """
        return whether or not this transaction has entries in different currencies
        """
        return len(self.faceCurrencies()) > 1 or len(self.postedCurrencies()) > 1

    def faceCurrencies(self):
        """
        return a tuple of the currencies represented in the transaction
        """
        currencies = {}
        for amt in map(lambda x: x.amount, self.entryValues()):
            currencies[amt.currency()] = True

        return currencies.keys()

    def postedCurrencies(self):
        """
        return a tuple of the currencies represented in the posted transaction
        """
        currencies = {}
        for amt in map(lambda x: x.amount, self.postedValues()):
            currencies[amt.currency()] = True

        return currencies.keys()

    def currencies(self):
        """
        return all the currencies in which this transaction can be historically valued in
        """
        currencies = self.faceCurrencies()
        for currency in self.postedCurrencies():
            if currency not in currencies:
                currencies.append(currency)

        return currencies
        
    def debitTotal(self, currency=''):
        """ sum all the debits """
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount > 0, self.entryValues()):
            total += entry.amountAs(base)

        return total
    
    def creditTotal(self, currency=''):
        """ sum all the credits - effective is for currency rate(s)"""
        base = currency or self.aq_parent.defaultCurrency()
        total = ZCurrency(base, 0.0)
        for entry in filter(lambda x: x.amount < 0, self.entryValues()):
            total += entry.amountAs(base)

        return total
    
    def total(self, currency=''):
        """ sum all the debits and credits - effective is for currency rate(s) """
        base = currency or self.aq_parent.defaultCurrency()
        return self.debitTotal(currency) + self.creditTotal(currency)

    def modificationTime(self):
        """ """
        return self.bobobase_modification_time().strftime('%Y-%m-%d %H:%M')

    def _status(self, state):
        BObjectManagerTree._status(self, state)
        self.reindexObject(idxs=['status'])

    def setReference(self, ob):
        if not self.reference:
            self._updateProperty('reference', '/'.join(ob.getPhysicalPath()))
            
    def setStatus(self, REQUEST=None):
        """
        does automatic status promotions - as all these functions are private :(
        """
        wftool = getToolByName(self, 'portal_workflow')
        status = self.status()

        base = self.defaultCurrency()

        if not len(self.objectIds()):
            if status != 'incomplete':
                self._status('incomplete')
            return

        if status == 'incomplete':
            if self.debitTotal(currency=base) == abs(self.creditTotal(currency=base)):
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.complete)
                status = self.status()
        elif status == 'complete':
            if self.debitTotal(currency=base) != abs(self.creditTotal(currency=base)):
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.incomplete)
                status = self.status()

        if status != 'reversed':
            posted = True
            for entry in self.entryValues():
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                except:
                    posted = False
                    break
            if posted:
                self._status('posted')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _updateProperty(self, name, value):
        BObjectManagerTree._updateProperty(self, name, value)
        if name in ('effective_date',):
            self.reindexObject(['effective_date'])
        if name == 'title':
            # go set untitled entries to this description ...
            for entry in self.entryValues():
                if not entry.title:
                    entry._updateProperty('title', value)

    def addEntries(self, entries):
        """
        Allow scripts to add entries ...
        """
        for e in entries:
            self._setObject(e.getId(), e)
            
    def createEntry(self, account, amount, title=''):
        """
        create an entry without having to worry about entry type
        """
        self.manage_addProduct['BastionLedger'].manage_addBLEntry(account, amount, title)

    def _setObject(self, id, object, roles=None, user=None, set_owner=1):
        #
        # auto-control the transaction status
        #
        assert object.meta_type in ('BLEntry', 'BLSubsidiaryEntry'), \
               "Must be derivative of BLEntry!"

        entry = None

        #
        # do some basic entry aggregation ...
        #
        matching = filter(lambda x: x.account == object.account, self.objectValues())
	if matching:
            entry = matching[0]
            LOG.debug( "%s::_setObject(%s) - aggregating" % (self.id, id))
            LOG.debug( entry)
	    # hmmm, this doesn't seem to mutate the underlying btree!!
            #entry += object
	    new = entry + object
            entry._updateProperty('amount', new.amount)
        else:
            LOG.debug( "%s::_setObject(%s) - new entry" % (self.id, id))
            object.txn = self.absolute_url(1)
            BObjectManagerTree._setObject(self, id, object, roles, user, set_owner)
            entry = self._getOb(id)

        # detect any fx mismatch and pin the amount - needed so debit/creditTotal works ...
        if object.amount.currency() != self.defaultCurrency():
            entry._setPostingAmount()

        self.setStatus()

    def _delObject(self, id, tp=1, suppress_events=False):
        #
        # auto-control the transaction status when entry is removed
        #
        BObjectManagerTree._delObject(self, id, tp, suppress_events)
        self.setStatus()

    def entries(self):
        """
        entryItems
        """
        return self.objectItems('BLEntry')

    def entryValues(self):
        """
        list of entries
        """
        return self.objectValues('BLEntry')

    def entryItems(self):
        """
        """
        return self.objectItems('BLEntry')

    def entry(self, account_id, ledger_id=''):
        """ retrieve an entry that should be posted to indicated account in indicated ledger"""
	for k, v in self.entries():
            if v.accountId() == account_id:
                if ledger_id == '' or v.blLedger().getId() == ledger_id:
                    return v
        return None

    def postedValues(self):
        """
        return the entries as represented in the posted account (and in the currency of that account)
        """
        if self.status() in ('posted',):
            results = []
            id = self.getId()
            for e in self.entryValues():
                try:
                    results.append(e.blAccount()._getOb(id))
                except (KeyError,AttributeError):
                    continue
            return tuple(results)
        return ()

    def manage_post(self, REQUEST=None):
        """
        post transaction entries  - note we do not post zero-amount entries!
        """
	status = self.status()

        if status in ('reversed', 'cancelled'):
            if REQUEST:
                return self.manage_main(self, REQUEST)
            return
        
        if status in ('incomplete', 'posted'):
            message = 'Transaction %s %s != %s' % (status, self.debitTotal(), self.creditTotal())
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return self.manage_main(self, REQUEST)
            raise AssertionError, "%s\n%s" % (message, str(self))

        try:
            map (lambda x: x._post(),
                 filter(lambda x: x.absAmount() > 0.005,
                        self.entryValues()))
        except PostingError:
            raise
        except:
            # raise a very meaningful message now!!
            typ, val, tb = sys.exc_info()
            fe=traceback.format_exception (typ, val, tb)
            raise AttributeError, '%s\n%s' % ('\n'.join(fe), str(self))

        # adjust status in index ...
        self._status('posted')
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def manage_toggle(self, ids=[], REQUEST=None):
        """
        flip the dr/cr on selected entries - useful to correct keying errors
        """
        if ids:
            for id, entry in filter(lambda x,ids=ids: x[0] in ids, self.entryItems()):
                entry._updateProperty('amount', -entry.amount)
            self.setStatus()

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_verify(self, forcefx=False, REQUEST=None):
        """
        verify the transaction has been applied correctly to the ledger(s)

        this function deliberately *does not* use the underlying object's methods
        to check this - it's supposed to independently check the underlying
        library - or consequent tamperings via the ZMI

        it returns a list of (Exception, note) tuples
        """
        bad_entries = []

        evs = self.entryValues()
        status = self.status()

        if status in ('posted', 'reversed'):
                
            #
            # make sure the transaction balanced (within 5 cents) in the first place ...
            #
            if abs(self.total()) > 0.05:
                bad_entries.extend(map(lambda x: (UnbalancedError(x), self.total()), evs))
            else:
                #
                # check that the posted entries are consistent with the balanced txn ...
                #
                base_currency = self.defaultCurrency()
                for  unposted in evs:
                    account = unposted.blAccount()
                    try:
                        posted = account._getOb(self.getId())
                    except:
                        # hmmm - dunno why we should have posted zero-amount transactions,
                        # but they're not wrong ...
                        if unposted.amount == 0:
                            continue
                        bad_entries.append((UnpostedError(unposted), ''))
                        continue

                    posted_amt = posted.amount
                    unposted_amt = unposted.amount

                    # find/use common currency base
                    if posted_amt.currency() != base_currency:
                        posted_amt = posted.amountAs(base_currency)

                    if unposted_amt.currency() != base_currency:
                        unposted_amt = unposted.amountAs(base_currency)

                    # 5 cent accuracy ...
                    if abs(posted_amt - unposted_amt) > 0.05:
                        bad_entries.append((IncorrectAmountError(unposted), 
                                            '%s - %s' % (posted_amt, posted_amt - unposted_amt)))

        #
        # we shouldn't be posting these ...
        #
        if status in ('cancelled', 'incomplete'):
            for entry in evs:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

        if status in ('complete'):
            for entry in evs:
                try:
                    posted = entry.blAccount()._getOb(self.getId())
                    bad_entries.append((PostingError(posted), ''))
                except:
                    continue

        if REQUEST:
            if bad_entries:
                REQUEST.set('manage_tabs_message',
                            '<br>'.join(map(lambda x: "%s: %s %s" % (x[0].__class__.__name__,
                                                                     html_quote(str(x[0].args[0])),
                                                                     x[1]), bad_entries)))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)

        return bad_entries

    def __getattr__(self, name):
        """
        returns the attribute or matches on title of the entries within ...
        """
        if not self._v_already_looking:
            try:
                #LOG.debug( "__getattr__(%s)" % name)
                self._v_already_looking = 1
                if self.__dict__.has_key(name):
                    return self.__dict__[name]

                # we are expecting just BLEntry deriviatives ...
                for entry in self.objectValues():
                    if entry.title == name:
                        return entry
            finally:
                self._v_already_looking = 0
        # not found - pass it on ...
        return Base.__getattr__(self, name)

    def manage_unpost(self, REQUEST=None):
        """
        remove effects of posting
        """
        for entry in self.entryValues():
            try:
                BObjectManagerTree._delObject(entry.blAccount(), self.getId())
            except KeyError:
                # hmmm - not found, but we need to overlook this to repair stuff ;)
                pass
        self._status('complete')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_beforeDelete(self, item, container):
        """ reverse any potential posting ... """
        LOG.debug('manage_beforeDelete(%s)' % self.getId())
        self.manage_unpost()
        # remove from catalog
        self.unindexObject()

    def manage_delObjects(self, ids=[], REQUEST=None):
        """
        remove entries - recalculating status
        """
        if ids:
            BObjectManagerTree.manage_delObjects(self, ids)
            self.setStatus()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_editProperties(self, REQUEST):
        """ Overridden to make sure recataloging is done """
        for prop in self._propertyMap():
            name=prop['id']
            if 'w' in prop.get('mode', 'wd'):
                value=REQUEST.get(name, '')
                self._updateProperty(name, value)

        self.reindexObject(idxs=['effective_date'])

    def editProperties(self, title, description, effective):
        """
        Plone form updates
        """
        self.title = title
        self.description = description
        self.effective_date = floor_date(effective)
        self.reindexObject()

    def indexObject(self, idxs=[]):
        """ Handle indexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = self.catalog()
            url = '/'.join(self.getPhysicalPath())
            cat.catalog_object(self, url, idxs)
        except:
            pass
        
    def unindexObject(self):
        """ Handle unindexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = self.catalog()
            url = '/'.join(self.getPhysicalPath())
            cat.uncatalog_object(url)
        except:
            pass

    def reindexObject(self, idxs=[]):
        if not idxs:
            self.unindexObject()
        self.indexObject(idxs)

    def notifyWorkflowCreated(self):
        # hmmm CMFCatalogAware causes our workflow to hang as our first
        # transition is AUTOMATIC ...
        pass
    
    def modifiable(self):
        """
        returns whether or not this transaction is still editable.  This means
        either in a non-posted state, or you've roles enough to repost it.
        """
        return self.status() in ('complete', 'incomplete') or \
            self.SecurityCheckPermission(ManageBastionLedgers)

    def manage_reverse(self, description='', effective=None, REQUEST=None):
        """
        create a reversal transaction
        """
        if self.status() != 'posted':
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Transaction not in Posted state!')
                return self.manage_main(self, REQUEST)
            return

        if not effective:
            effective = self.effective_date

        tid = manage_addBLTransaction(self.aq_parent,
                                      title=description or 'Reversal: %s' % self.title,
                                      effective=effective,
                                      ref=self)
        txn = self.aq_parent._getOb(tid)

        for id,entry in self.entryItems():
            e = entry._getCopy(entry)
            e.amount = entry.amount * -1
            e.title = 'Reversal: %s' % entry.title
            # ensure the new entry does proper fx ...
            if getattr(entry, 'posted_amount', None):
                e.posted_amount = entry.posted_amount * -1
            txn._setObject(id, e)

        # we don't want any of these entries included in future calculations ...

        txn.manage_post()
        txn._status('postedreversal')
        
        self.setReference(txn)
	self._status('reversed')

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_cancel(self, REQUEST=None):
        """
        cancel a transaction
        """
        status = self.status()
        if status in ('incomplete', 'complete'):
            self._status('cancelled')
        else:
            raise InvalidTransition, 'cancel'
        
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_repost(self, force=False, REQUEST=None):
        """
        hmmm, sometimes/somehow stuff gets really f**ked up ...

        we also post complete txns - which could be processed via manage_post

        force causes fx/posted amounts to be recalculated
        """
        status = self.status()
        if status in ('posted', 'complete'):
            for entry in self.entryValues():
                try:
                    #if entry.absAmount() > 0.005:
                    entry._post(force=force)
                except PostingError:
                    raise
        if REQUEST:
            return self.manage_main(self, REQUEST)
        
        
    def manage_statusModify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        try:
            self.content_status_modify(workflow_action)
        finally:
            pass

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)

    def __str__(self):
        """ useful for debugging ... """
        return "<%s instance %s (%s) - %s>" % (self.meta_type, self.getId(),self.status(),
                                          str( map( lambda x: str(x), self.entryValues() ) ) )

    def asCSV(self, datefmt='%Y/%m/%d', REQUEST=None):
        """
        """
        return '\n'.join(map(lambda x: x.asCSV(datefmt), self.entryValues()))


    def _repair(self):
	if self.__dict__.has_key('status'):
	    status = self.__dict__['status']
	    if status == 'Unposted':
		status = 'complete'
	    else:
		status = status.lower()
	    self._status(status)
            self.indexObject()
	    del self.__dict__['status']
	    
        map( lambda x:x._repair(), self.objectValues() )

    def manage_migrateFX(self, REQUEST=None):
        """
        in the past, we posted the fx rate into the fx_rate attribute of the posted entry
        now, we're actually going to post the txn's entry amount into the posted entry
        """
        if self.isMultiCurrency():
            # recalculate fx_rate
            self.manage_repost(force=True)

            for id, entry in self.entries():
                posted_amount = getattr(aq_base(entry),'posted_amount', None)
                if posted_amount:
                    delattr(entry, 'posted_amount')

            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Fixed up FX')
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Non-FX transaction - nothing to do')

        if REQUEST:
            return self.manage_main(self, REQUEST)
    
AccessControl.class_init.InitializeClass(BLTransaction)

class BLTransactions( BTreeFolder2, ZCatalog ):
    """ A Transaction Folder - actually now just a specialised cataloging tool """

    meta_type = 'BLTransactions'

    __ac_permissions__ = BTreeFolder2.__ac_permissions__ + ZCatalog.__ac_permissions__

    manage_options =  ZCatalog.manage_options

    index_html = None

    def all_meta_types(self): return ()
    
    def __init__(self, id, title=''):
        BTreeFolder2.__init__(self, id)
        ZCatalog.__init__(self, id)
        self.title = title
        self.addIndex('status', 'FieldIndex')
        #class extra:
        #    since_field="effective_start"
        #    until_field="effective_end"
        #self.addIndex('effective_date', 'DateRangeIndex', extra())
        self.addIndex('effective_date', 'DateIndex')
        self.addIndex('entered_by', 'FieldIndex')
        self.addIndex('meta_type', 'FieldIndex')
        self.addColumn('meta_type')


    def __len__(self):
        return len(self._catalog.indexes.get('effective_date', []))

    def __call__(self, REQUEST=None, *args, **kw):
        """
	returns a list of BLTransaction (derivatives) meeting the search criteria,
        wrapping ZCatalog.searchResults() excepting returning objects instead of brains ...
	"""
        return map(lambda x:x.getObject(), self.searchResults(REQUEST, *args, **kw))

    # this function is used in manage_catalogView and needs to be reliable ...
    def searchResults(self, REQUEST=None, *args, **kw):
        """
	returns a list of BLTransaction (derivatives) meeting the search criteria,
        wrapping ZCatalog.searchResults()
	"""
        if REQUEST is not None:
            if type(REQUEST) == type({}):
                criteria = dict(REQUEST)
            else:
                criteria = dict(REQUEST.form)
        else:
            criteria = {}
        criteria.update(kw)
        criteria['meta_type'] = self.aq_parent.transaction_types
        return ZCatalog.searchResults(self, REQUEST=criteria)

    def manage_catalogFoundItems(self, REQUEST=None):
        """
        *only* catalog transactions (ie no entries)
        """
        for txn in filter(lambda x: isinstance(x, BLTransaction), 
                          self.aq_parent.objectValues()):
            url = '/'.join(txn.getPhysicalPath())
            self.catalog_object(txn, url)
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _clone(self, date=DateTime()):
        """
        return a copy of itself - used for rollover/archiving
        """
        ob = self._getCopy(self)
        return ob

    def _purge(self, date=DateTime()):
        """
        remove all transactions older than date - does not invoke manage_beforeDelete
        consistency enforcing stuff ...
        """
        for txn in self.searchResults(meta_type={'query':['BLTransaction', 'BLSubsidiaryTransaction']},
                                      effective_date={'query':date, 'range':'max'}):
            self.aq_parent._delOb(txn.getId())

    def _repair(self):
        try:
            self.addColumn('meta_type')
        except:
            pass
        try:
            self.addIndex('meta_type', 'FieldIndex')
        except:
            pass
        # force clearing down of bad data ...
	self._catalog.migrate__len__()
	

AccessControl.class_init.InitializeClass(BLTransactions)


def delTransaction(ob, event):
    #if ob.status() not in ('cancelled', 'incomplete') and not ob.expertMode():
    #    raise BeforeDeleteException, 'you cannot delete posted transactions (%s)!' % ob.absolute_url()

    for entry in ob.entryValues():
        account = entry.blAccount()
        if account:
            try:
                BObjectManagerTree._delObject(account, ob.getId())
            except KeyError:
                # hmmm - not found, but we need to overlook this to repair stuff ;)
                pass
    # remove from catalog
    ob.unindexObject()

