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

# import stuff
import AccessControl, os, types, operator, Acquisition, string, sys, traceback
from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens, manage_properties, \
    access_contents_information
from AccessControl.users import BasicUser
from OFS.userfolder import manage_addUserFolder
from DateTime import DateTime
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import BeforeDeleteException
from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import logging

from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES
from Products.BastionBanking import ZReturnCode

from utils import floor_date, ceiling_date, assert_currency
from BLBase import *
from BLAccount import BLAccounts, date_field_cmp, addBLAccount
from BLSubsidiaryLedger import BLSubsidiaryLedger
from BLEntry import manage_addBLEntry
from BLSubsidiaryEntry import manage_addBLSubsidiaryEntry
from BLInventory import BLInventory
from BLSubsidiaryAccount import BLSubsidiaryAccount
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Permissions import ManageBastionLedgers, OperateBastionLedgers, OverseeBastionLedgers
from BLAttachmentSupport import BLAttachmentSupport
from BLProcess import manage_addBLProcess
from BLTransactionTemplate import manage_addBLTransactionTemplate
from BLEntryTemplate import manage_addBLEntryTemplate
from Exceptions import AlreadyPostedError, PostingError, LedgerError, InvalidState

from zope.interface import Interface, implements

class IOrder(Interface): pass
class ICashBook(Interface): pass

LOG = logging.getLogger('BLOrderBook')

def addBLOrderBook(self, id, title='', REQUEST=None):
    """
    Plone-based entry
    """
    inventory_id = self.bastionLedger().objectIds('BLInventory')[0]
    control = addBLAccount(self.Ledger, id, title)
    self.manage_addBLOrderBook(id, control, inventory_id, 'Q', title)
    return id

manage_addBLOrderBookForm = PageTemplateFile('zpt/add_orderbook', globals()) 
def manage_addBLOrderBook(self, id, controlAccount, inventory,
                          prefix='Q', title='', REQUEST=None):
    """ adds an orderbook """
    try:
        # do some checking ...
        control = self.Ledger._getOb(controlAccount)
        assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
        assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."

        self._setObject(id, BLOrderBook(id, title, control, inventory, ['BLOrderAccount'],
                                        self.Ledger.currencies, prefix))
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

class BLOrderBook ( BLSubsidiaryLedger ):
    """ """
    meta_type = portal_type = 'BLOrderBook'

    __ac_permissions__ = BLSubsidiaryLedger.__ac_permissions__ + (
        (access_contents_information, ('orderValues', 'orderStatuses')),
        (view_management_screens, ('manage_accounts', 'manage_transactions', 'manage_Reports', 
                                   'manage_orders',)),
        (OperateBastionLedgers, ('edit', 'nextOrderNo', 'manage_postOrder', )),
        (ManageBastionLedgers, ('manage_edit',)),
	(view, ('isReceivable', 'isPayable', 'blInventory', 'totalTaxInclusiveAmount',
		'totalTaxExclusiveAmount', 'totalAmount', )),
        )

    _properties = BLSubsidiaryLedger._properties + (
        {'id':'inventory',    'type':'selection', 'mode':'w', 'select variable':'InventoryIds'},
        {'id':'instructions', 'type':'text',       'mode':'w'},
        )

    account_types = ('BLOrderAccount',)

    # hmmm - a late addition ...
    instructions = ''
    
    manage_options = BLSubsidiaryLedger.manage_options[0:4] + (
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('BastionLedger', 'orderbook.stx')},
    ) + BLSubsidiaryLedger.manage_options[5:]

    def InventoryIds(self):
        return map(lambda x: x.getId(), self.inventoryValues())

    #manage_main = PageTemplateFile('zpt/view_orders', globals())
    manage_orders = PageTemplateFile('zpt/view_orders', globals())
    manage_propertiesForm = PageTemplateFile('zpt/orderbook_props', globals())
    
    
    def __init__(self, id, title, control, inventory, currencies, order_prefix='Q',
                 account_prefix='A', txn_prefix='T' ):
        self.order_prefix = order_prefix
        self.order_no = 1
        # think inventory is just the id of the BLInventory object ...
        #assert isinstance(inventory, BLInventory), "Incorrect Inventory Type"
        self.inventory = inventory
        BLSubsidiaryLedger.__init__(self, id, title, control, currencies,
                                    1000000, account_prefix, 1, txn_prefix )
        self.instructions = ''

    def orderStatuses(self):
        """
        return a list of status ids associated with order workflow
        """
        return getToolByName(self, 'portal_workflow').blorder_workflow.states.objectIds()

        
    def orderValues(self, entered_by=[], orderdate=[], status=[], **kw):
        """
        returns a list of BLOrder objects meeting the criteria
        """
        orders = []
        for account in self.accountValues(**kw):
            orders.extend(account.orderValues(entered_by, orderdate, status))
        return orders

    def isReceivable(self):
        return self.controlAccount().type == 'Asset'

    def isPayable(self):
        return self.controlAccount().type == 'Liability'

    def manage_edit(self, title, description, txn_id, account_id, account_prefix,
                    txn_prefix, currencies, email='',  REQUEST=None):
        """
        update orderbook properties
        """
        # do some bodgy stuff here ...
        request = self.REQUEST
        
        self.inventory = request.get('inventory', self.InventoryIds()[0])
        self.instructions = request.get('instructions', '')

        return BLSubsidiaryLedger.manage_edit(self, title, description, txn_id, account_id, account_prefix,
                                              txn_prefix, currencies, email, REQUEST)
    

    def nextOrderNo(self):
        """
        generate the order number
        """
        id = str(self.order_no)
        self.order_no += 1
        return "%s%s" % (self.order_prefix, string.zfill(id, 10))

    def blInventory(self):
        """
        return the Inventory from which to order parts against
        """
        try:
            return getattr(self.aq_parent, self.inventory)
        except:
            raise AttributeError, 'Inventory not found: %s' % self.inventory

    def manage_postOrder(self, order, REQUEST=None):
        """
        take an order and turn it into a transaction and post it ...
        """
        if order.getNet() == 0:
            return

        #
        # ignore Process driver - call txn directly
        #
        transaction = self.blp_order.generate(order.blAccount(),
                                              order,
                                              title = order.title,
                                              effective=floor_date(order.orderdate))

        # this shouldn't happen but we're getting in all kinds of crap posting cashbook orders
        # via manage_pay ...
        if not transaction.status() == 'posted':
            try:
                transaction.manage_post()
            except AlreadyPostedError:
                pass

        for orderitem in order.objectValues('BLOrderItem'):
            #
            # fix the price in the order - it is floating based on inventory until then ...
            #
            orderitem.amount = orderitem.calculateNetPrice()
            orderitem.blPart().onhand =- orderitem.quantity
        
        # assign txn to order for backwards reference ...
        order.txn_id = transaction.getId()
        transaction.setReference(order)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def totalTaxInclusiveAmount(self, datemin, datemax):
        obs = map ( lambda x: x.getObject(),
                    self.catalog( orderdate = { 'query': [datemin, datemax], 'range':'minmax' },
                                               status = {'query': 'invoiced' } ) )
        if obs:
            return reduce( operator.add, map ( lambda x: x.getGross(),
                                               filter(lambda x: x.taxincluded, obs) ) )
        else:
            return ZCurrency(self.currencies[0], 0)


    def totalTaxExclusiveAmount(self, datemin, datemax):
        obs = map ( lambda x: x.getObject(),
                    self.catalog( orderdate = { 'query': [datemin, datemax], 'range':'minmax' },
                                               status = {'query': 'invoiced' } ) )

        if obs:
            return reduce( operator.add, map ( lambda x: x.getGross(),
                                               filter(lambda x: not x.taxincluded, obs) ))          
        else:
            return ZCurrency(self.currencies[0], 0)

    def totalAmount(self, datemin, datemax):
        LOG.debug( "BLOrderBook::totalAmount() cat = %s" % str( self.catalog( status = {'query':'invoiced'} ) ))
        amts = map ( lambda x: x.getObject().getGross(),
                    self.catalog( orderdate = { 'query': [datemin, datemax], 'range':'minmax' },
                                  status = {'query':'invoiced'} ))

        LOG.debug( "BLOrderBook::totalAmount(%s, %s) amts = %s" % ( datemin, datemax, str(amts) ))
        if amts:
            return reduce( operator.add, amts )          
        else:
            return ZCurrency(self.currencies[0], 0)

    def _repair(self):
        BLSubsidiaryLedger._repair(self)
        # new FSProcess-based postOrder ...
        if self.__dict__.has_key('_reserved_names'):
            del self.__dict__['_reserved_names']
        # hmmm - if we've ZODB'd our propmap ...
        if not self.hasProperty('instructions'):
            self._properties=self._properties + (
                {'id':'instructions', 'type':'text', 'mode':'w'},)
        if not self.hasProperty('inventory'):
            self._properties = self._properties + (
                {'id':'inventory', 'type':'selection', 'mode':'w', 'select variable':'InventoryIds'},)
            self.inventory = self.aq_parent.objectIds('BLInventory')[0]

AccessControl.class_init.InitializeClass(BLOrderBook)


def addBLOrderAccount(self, id, title='', REQUEST=None):
    """
    Plone adding of order account from ledger
    """
    id = self.manage_addBLOrderAccount(id=id, title=title)
    return id
    
manage_addBLOrderAccountForm = PageTemplateFile('zpt/add_orderaccount', globals()) 
def manage_addBLOrderAccount(self,id='', title='', description='', currency='', uid='', pwd='', REQUEST=None):
    """
    a customer/vendor

    if uid is a User, then change ownership of the account
    if uid/pwd present, then set up an acl_users and change account ownership
    """
    #assert isinstance(self.this(), BLAccounts), 'Wrong Container Type: %s' % self.meta_type
    if not currency:
        currency = self.defaultCurrency()
    assert currency in CURRENCIES, 'Unknown currency: %s' % currency
    if not id:
        id = self.nextAccountId()
    type = self.controlAccount().type
    self._setObject(id, BLOrderAccount(id, title, description, type, currency))

    account = self._getOb(id)

    if uid:
        if type(uid) == types.StringType and pwd:
            manage_addUserFolder(account)
            account.acl_users.userFolderAddUser(uid, pwd, [], [])
            user = account.acl_users.getUser(uid)
        else:
            assert isinstance(uid, BasicUser), 'uid not a User!!'
            user = uid
        account.changeOwnership(user)
        account.manage_setLocalRoles(id, ['Owner'])

    bt = getToolByName(self, 'portal_bastionledger')
    if bt.hasTaxTable('sales_tax'):
        account.manage_addTaxGroup('sales_tax')

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_details" % (REQUEST['URL3'], id))

    return id


class BLOrderAccount(BLSubsidiaryAccount):
    """
    This class encompasses the concept of an orderbook's accounts.

    These accounts have additional information necessary to ship goods and
    include facilities to retain payment information.
    
    """
    meta_type = portal_type = 'BLOrderAccount'

    __ac_permissions__ = BLSubsidiaryAccount.__ac_permissions__ + (
        (access_contents_information, ('orderValues',)),
        (view_management_screens, ('manage_statement', 'getOrder',
                                   'acl_item', )),
        (OperateBastionLedgers, ('manage_invoiceObjects','manage_finishObjects',
				 'generateUniqueId','manage_addOrder',
                                 'manage_oaEdit')),
        (OverseeBastionLedgers, ('manage_cancelObjects',)),
	(view, ('entries', 'manage_payAccount', )),
        )

    _properties = BLSubsidiaryAccount._properties + (
        {'id':'contact',       'type':'string',   'mode':'w'},
        {'id':'address',       'type':'text',     'mode':'w'},
        {'id':'phone',         'type':'string',   'mode':'w'},
        {'id':'fax',           'type':'string',   'mode':'w'},
        {'id':'discount',      'type':'float',    'mode':'w'},
        {'id':'creditlimit'  , 'type':'currency', 'mode':'w'},
        {'id':'taxincluded',   'type':'boolean',  'mode':'w'},
        {'id':'terms',         'type':'int',      'mode':'w'},
        {'id':'notes',         'type':'text',     'mode':'w'},
        {'id':'shiptoname',    'type':'string',   'mode':'w'},
        {'id':'shiptoaddress', 'type':'text',     'mode':'w'},
        {'id':'shiptocontact', 'type':'string',   'mode':'w'},
        {'id':'shiptophone',   'type':'string',   'mode':'w'},
        {'id':'shiptofax',     'type':'string',   'mode':'w'},
        {'id':'shiptoemail',   'type':'string',   'mode':'w'},
        )

    def manage_options(self):
	options = [
        {'label': 'Statement',     'action': 'manage_statement',
          'help':('BastionLedger', 'orderaccount.stx') },
        {'label': 'View',  'action': '',},
        {'label': 'Orders',  'action': 'manage_main',
         'help':('BastionLedger', 'orderstmt.stx') },
        {'label': 'Details',    'action': 'manage_details' } ]
	options.extend( BLSubsidiaryAccount.manage_options(self)[3:])
	return tuple(options)

    #index_html = PageTemplateFile('zpt/orderaccount_index', globals())
    manage_main = PageTemplateFile('zpt/view_orders', globals())
    manage_details   = PageTemplateFile('zpt/edit_orderaccount', globals())
    # hmmm - this was only to apply Bastion Merchant Services payment form ...
    #manage_statement = PageTemplateFile('zpt/view_orderaccount', globals())
    #manage_statement._setName('manage_statement')

    def filtered_meta_types(self, user=None):
        if self.status() in ('open', 'healthy'):
	    return [ ProductsDictionary('BLOrder') ]
        return []

    def __init__(self, id, title, description, type, currency, email='', contact='', address='',
                 phone='', fax='', discount=0,
                 taxincluded=0, terms=7, creditlimit=None, notes='', shiptoname='', shiptoaddress='',
                 shiptocontact='', shiptophone='', shiptofax='', shiptoemail=''):
        BLSubsidiaryAccount.__init__(self, id, title, description, type, 'OrderBook', currency, id)
        self.opened = DateTime()
	if not creditlimit:
	    creditlimit = ZCurrency(currency, 0)
        BLOrderAccount.manage_oaEdit(self, title, description, email, contact, address,  phone, fax, discount,
                                     creditlimit, terms, notes, shiptoname, shiptoaddress,
                                     shiptocontact, shiptophone, shiptofax, shiptoemail, taxincluded)

    def manage_oaEdit(self, title, description, email, contact, address,  phone, fax, discount=0,
                      creditlimit=0, terms=7, notes='', shiptoname='', shiptoaddress='',
                      shiptocontact='', shiptophone='', shiptofax='', shiptoemail='',
                      taxincluded=False, REQUEST=None):
        """ 
        """
        self.title = title
        self.description = description
        self.email = email
        self.contact = contact
        self.address = address
        self.phone = phone
        self.fax = fax
        self.discount = float(discount)
        self.taxincluded = bool(taxincluded)
        self.terms = int(terms)
	assert creditlimit.__class__.__name__ == 'ZCurrency', 'creditlimit not a ZCurrency: %s' % creditlimit.__class__.__name__
        self.creditlimit = creditlimit
        self.notes = notes
        self.shiptoname = shiptoname 
        self.shiptoaddress = shiptoaddress
        self.shiptocontact = shiptocontact
        self.shiptophone = shiptophone
        self.shiptofax = shiptofax
        self.shiptoemail = shiptoemail
        self.bank_account = ''

        if REQUEST:
            REQUEST.set('management_view', 'Details')
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_details(self, REQUEST)

    def entries(self, effective=None, status=['posted',]):
	"""
	just return active entries as this is a user-account and we don't want them
	to see all the cancellations/reversals etc ...
	"""
	# TODO - we'd like to do this, but ....
        #result = list( filter(lambda x: x[1].status() == 'posted',
        #               self.objectItems('BLSubsidiaryEntry')) )
	result = []
	for k,v in self.objectItemsByDate('BLSubsidiaryEntry', effective or DateTime()):
	    try:
	        if v.status() in status:
		    result.append((k,v))
            except:
		raise
		raise TypeError, k

        #result.sort(date_field_cmp)
	return result

    # inherit these!!
    def X__str__(self):
        return str(self.__dict__)

    def X___repr__(self):
        return str(self.__dict__)

        
    def manage_invoiceObjects(self, ids=[], REQUEST=None):
        """ """
        for id in ids:
            order = self._getOb(id)
	    if order.status() == 'open':
                order.manage_invoice()
            
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_finishObjects(self, ids=[], REQUEST=None):
        """
        go complete these orders - this may mean payment(s) have been assigned etc etc
        """
        for id in ids:
            order = self._getOb(id)
            try:
                order.content_status_modify(workflow_action='finish')
            except:
                pass

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_delObjects(self, ids=[], force=0, REQUEST=None):
        """ """
        # only remove incomplete orders (or BLEntry's - as allowed by BLAccount...)
        if type(ids) == types.StringType:
            ids = [ ids ]
        for ob in map(lambda x,y=self: y._getOb(x), ids):
            if force:
                self._delObject(ob.getId(), force=force)
            else:
                #if not isinstance(ob, BLOrder) or ob.status() in ('incomplete', 'uninvoiced'):
                self._delObject(ob.getId())
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Deleted')
            return self.manage_main(self, REQUEST)

    def manage_cancelObjects(self, ids=[], REQUEST=None):
        """ """
        for id in ids:
            self._getOb(id).manage_cancel()
            
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def manage_payAccount(self, amount=None, REQUEST=None):
        """
        create a payment transaction, but don't actually post it
        this is needed for BastionMerchantService's which do asynchronous
        RPC :(
        """
        if not amount:
            amount = self.balance()
        try:
            if type(amount) == types.StringType:
                amount = ZCurrency(self.base_currency, float(amount))
        except Exception, e:
            message = "Not a valid amount: %s" % e
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return self.manage_statement(self, REQUEST)
            raise AttributeError, message

        if amount != 0:
            BLSubsidiaryAccount.manage_payAccount(self, 
                                                  amount,
                                                  self.Ledger.accountsForTag('order_payments')[0])

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Payment Processed')
            return self.manage_main(self, REQUEST)
        
    def getOrder(self, txn_id):
        reference = self._getOb(txn_id).reference
        if reference is not None and getattr(self, reference, None):
            return getattr(self, reference)
        return None

    def manage_addOrder(self, title='', orderdate=None, reqdate=None, taxincluded=False, discount=0.0, 
                        REQUEST=None):
        """ adds an order - but without needing to use the BLOrder add page template ..."""
        id = self.aq_parent.nextOrderNo()
        self._setObject(id, BLOrder(id, 
                                    title, 
                                    orderdate=orderdate or DateTime(),
                                    reqdate=reqdate or DateTime() + 7,
                                    taxincluded=taxincluded, 
                                    discount=discount))
        order = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (self.getId(), order.getId()))
        return order
    
    def _delObject(self, id, tp=1, suppress_events=False,force=0):
        if force:
            BObjectManagerTree._delObject(self, id, tp, suppress_events=suppress_events)
            return

        ob =  self._getOb(id)
        if ob.meta_type == 'BLOrder' or ob.getId() == 'acl_users':
            BObjectManagerTree._delObject(self, id, tp, suppress_events=suppress_events)

    def acl_item(self):
        return getattr(aq_base(self), 'acl_users', None)

    def generateUniqueId(self, type_name=None):
        """
        TODO - future potential ...
        """
        if type_name in ['BLOrder', 'BLCashOrder']:
            return self.nextOrderNo()
        return BLSubsidiaryAccount.generateUniqueId(self, type_name)

    def orderValues(self,entered_by=[], orderdate=[], status=[], **kw):
        """
        returns a list of BLOrder objects meeting the criteria
        """
        orders = self.objectValues(('BLOrder', 'BLCashOrder'))

        if orderdate:
            orders = filter(lambda x: x.orderdate >= min(orderdate) and x.orderdate <= max(orderdate), orders)
            
        if status:
            orders = filter(lambda x: x.status() in status, orders)

        return orders


    def _repair(self):
        BLSubsidiaryAccount._repair(self)
        if not getattr(aq_base(self), 'notes', None):
            self.notes = ''
	if type(self.address) == type([]):
	    self.address = '\n'.join(self.address)
	if type(self.shiptoaddress) == type([]):
	    self.shiptoaddress = '\n'.join(self.shiptoaddress)
	if not type(self.creditlimit) == ZCurrency:
	    try:
	        self.creditlimit = ZCurrency(self.base_currency, self.creditlimit)
	    except:
	        # maybe it's our old Currency class ...
		self.creditlimit = ZCurrency(self.base_currency, 0)
        map( lambda x: x._repair(), self.objectValues('BLOrder') )

        # hmmm - we seem to have some old shite lying around ...
        if self.__dict__.has_key('_properties'):
            props = self.__dict__['_properties']
            del self.__dict__['_properties']
                
        if self.__dict__.has_key('__allow_groups__'):
            del self.__dict__['__allow_groups__']
            
AccessControl.class_init.InitializeClass(BLOrderAccount)

manage_addBLOrderItemForm = PageTemplateFile('zpt/add_orderitem', globals()) 
def manage_addBLOrderItem(self, part, title='', qty=1, unit=0, discount=0.0, amount=None, REQUEST=None):
    """ 
    an order line within an Order 
    
    you can specifically override the order discount on the orderline
    """

    realself = self.this()
    if not isinstance(realself, BLOrder):
        raise LedgerError, "Cannot add a BLOrderItem to this type: %s" % self.meta_type
    try:
        qty = float(qty)
    except:
        raise ValueError, """ Quantity is not numeric! """

    if discount > 100.0 or discount < 0.0:
        raise ValueError, """ Discount is expressed as a decimal! """
        
    if not getattr(part, 'meta_type', None):
        realpart = realself.blInventory().blPart(part)
    else:
	realpart = part

    assert realpart and realpart.meta_type == 'BLPart', "Part not found: %s" % part

    if not unit:
        if realself.isSell():
            unit = realpart.sellprice
        else:
            unit = realpart.listprice
            
    effective = ceiling_date(self.orderdate)

    # do any FX adjustment on the unit price ...
    base_currency = self.aq_parent.base_currency
    if unit._currency != base_currency:
        if self.aq_parent.blLedger().isReceivable():
            rate = 1.0 / self.portal_bastionledger.crossBuyRate(base_currency, unit._currency, effective)
        else:
            rate = self.portal_bastionledger.crossSellRate(base_currency, unit._currency, effective)            
        unit = ZCurrency(base_currency, rate * unit._amount)

    if amount and amount._currency != base_currency:
        if self.aq_parent.blLedger().isReceivable():
            rate = 1.0 / self.portal_bastionledger.crossBuyRate(base_currency, amount._currency, effective)
        else:
            rate = self.portal_bastionledger.crossSellRate(base_currency, amount._currency, effective)            
        amount = ZCurrency(base_currency, amount._amount * rate)
    #
    # cycle thru some numbers until we find  a good one ...
    #
    not_added = 1
    if self.objectIds():
            id = int( max(self.objectIds() ) ) + 1
    else:
        id = 1
    while not_added:
        try:
            #LOG.debug('%s %f * %s' % (part, qty, unit))
            item = BLOrderItem(str(id), realpart, unit, title, qty, discount, amount)
            self._setObject(str(id), item)
            not_added = 0
        except:
            typ, val, tb = sys.exc_info()
            if str(typ) in ('BadRequest', 'Bad Request', 'zExceptions.BadRequest'):
                # TODO: a messagedialogue ..
                id += 1
            else:
                raise
        
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    else:
        return self._getOb(str(id))

class BLOrderItem(PropertyManager, BSimpleItem):
    """
    An order item is expected to have either a part existing in the inventory,
    or to be primed with an amount
    """
    meta_type = portal_type = 'BLOrderItem'

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (OperateBastionLedgers, ('manage_edit', 'setReference',)),
        (view, ('getReference', 'calculateGrossPrice', 'calculateNetPrice',
                'calculateCost', 'blPart', 'getReference',)),
        ) + BSimpleItem.__ac_permissions__

    _properties = PropertyManager._properties + (
        {'id':'part_id',       'type':'string',   'mode': 'r',},
        {'id':'unit',          'type':'currency', 'mode': 'w',},
        {'id':'quantity',      'type':'float',    'mode': 'w',},
        {'id':'discount',      'type':'float',    'mode': 'w',},
        {'id':'amount',        'type':'currency', 'mode': 'w',},
        {'id':'note',          'type':'text',     'mode': 'w',},
        {'id':'ref',           'type':'string',   'mode': 'w',},
        )
	
    ref = ''
    manage_options = PropertyManager.manage_options + BSimpleItem.manage_options

    manage_main = PropertyManager.manage_propertiesForm
    manage_main._setName('manage_propertiesForm')

    def __init__(self, id, part, unit, title='', quantity=1.0, discount=0.0, amount=None):
        self.id = id
        if title == '':
            title = part.title_and_id()
        try:
            self.part_id = part.getId()
        except:
            self.part_id = None
	self.ref = ''
        self.manage_edit(title, quantity, discount, unit, amount, '')

    def manage_edit(self, title, quantity, discount=0.0, unit=None, amount=None, note='', REQUEST=None):
        """
        """
        self.title = title
        self.quantity = abs(float(quantity))
        self.discount = abs(float(discount) / 100.0)
        if unit:
            try:
                assert_currency(unit)
            except:
                unit = ZCurrency(unit)
            self.unit = unit
        else:
            self.unit = None
        if amount:
            self.amount = abs(amount)
        else:
            self.amount = None
	self.note = note
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
        return 0

    def calculateNetPrice(self):
        """
        return price with discounts/price policy applied
        """
        if getattr(aq_base(self), 'amount', None):
            return self.amount

        account = self.aq_parent.blAccount()

        # acquire parent discount (if set)
        discount = self.discount or self.aq_parent.discount

        return self.calculateGrossPrice() * (1.0 - discount)

    def calculateGrossPrice(self):
        """
        return total undiscounted price
        """
        return self.unit * self.quantity
        
    def calculateCost(self):
        """
        work out the cost of an order item 
        """
        return self.blPart().listprice * self.quantity

    def blPart(self):
        """ orderitem in order in account in orderbook .... - unless it's in a BLQuote..."""
        return self.aq_parent.blInventory().blPart(self.part_id)

    def setReference(self, ref):
        """
        optionally store a reference to something
        """
        self.ref = ref

    def getReference(self):
        """
        return the object referenced or the reference itself
        """
        if getattr(aq_base(self), 'ref', None):
            try:
                return self.restrictedTraverse(self.ref)
            except:
                return self.ref
        return None

    def getIcon(self, relative_to_portal=False):
        return self.blPart().getIcon(relative_to_portal)

    def _repair(self):
        if not getattr(aq_base(self), 'unit', None):
            self.unit = self.blPart().sellprice
        if not getattr(aq_base(self), 'note', None):
	    self.note = ''
        amount = getattr(aq_base(self), 'amount', None)
        if amount:
            try:
                assert_currency(amount)
            except:
                try:
                    self.amount = ZCurrency(amount)
                except TypeError:
                    # hmmm - it's really f**ked!!
                    self.amount = ZCurrency(self.aq_parent.aq_parent.base_currency, 0)

AccessControl.class_init.InitializeClass(BLOrderItem)

manage_addBLOrderForm = PageTemplateFile('zpt/add_order', globals())                                         
def manage_addBLOrder(self, id='', title='', orderdate=DateTime(), taxincluded=False, 
                      notes='', contact='', email='', discount=0.0, REQUEST=None):
    """
    adds an order (Plonfied)
    """
    if not id:
        id = self.nextOrderNo()

    self._setObject(id, BLOrder(id, 
                                title, 
                                orderdate=orderdate, 
                                taxincluded=taxincluded, 
                                discount=discount,
                                notes=notes,
                                contact=contact,
                                email=email))
 
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id ))

    # Plone requires this ...
    return id

manage_addBLCashOrderForm = PageTemplateFile('zpt/add_cashorder', globals())                                         
def manage_addBLCashOrder(self, id='', title='', orderdate=DateTime(), taxincluded=False, 
                          discount=0.0, notes='', REQUEST=None):
    """
    adds an order (Plonfied)

    Note we automagically figure out if it should be cash or charge ...
    """
    if not id:
        id = self.nextOrderNo()

    self._setObject(id, BLCashOrder(id, title, orderdate=orderdate, 
                                    taxincluded=taxincluded, discount=discount, 
                                    notes=notes))

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id ))

    # Plone requires this ...
    return id


def addBLOrder(self, id, title=''):
    """
    Plone order creation from an order account
    """
    id = self.manage_addBLOrder(id=id,
                                title=title,
                                orderdate=DateTime(),
                                taxincluded=self.taxincluded,
                                notes=self.instructions,
                                email=self.email,
                                contact=self.contact)
    return id

def addBLCashOrder(self, id, title=''):
    """
    Plone cash order creation
    """
    id = manage_addBLCashOrder(self,
                               id=id,
                               title=title,
                               orderdate=DateTime(),
                               taxincluded=self.taxincluded,
                               notes=self.instructions)
    return id

class BLOrder(BObjectManager, PropertyManager, BLAttachmentSupport):
    """
    A purchase/sales request
    """    
    meta_type = portal_type = 'BLOrder'

    implements(IOrder)

    __ac_permissions__ = BObjectManager.__ac_permissions__ + (
        (access_contents_information, ('blTransaction', 'blAccount')),
        (view, ('orderItemValues', 'modifiable', 'index_html', 
		'getGross', 'getNet', 'getTax', 'getDiscount', 'calculateTax', 'status', 
		'modifiable', 'modificationTime', 'availableParts', 
		'isOpen', 'blTransaction', 'weight', 'isBuy', 'isSell')),
        (OperateBastionLedgers, ('manage_edit', 'setStatus', 'manage_status_modify',
				 'manage_emailInvoice', 'manage_invoice', 'manage_finish')),
        (OverseeBastionLedgers, ('manage_cancel',)),
        ) + PropertyManager.__ac_permissions__ + BLAttachmentSupport.__ac_permissions__

    shiptophone = ''
    shiptofax = ''

    _properties = PropertyManager._properties + (
        {'id':'orderdate',     'type':'date',    'mode':'w'},
        {'id':'reqdate',       'type':'date',    'mode':'w'},
        {'id':'notes',         'type':'text' ,   'mode':'w'},
	{'id':'taxincluded',   'type':'boolean', 'mode':'w'},
	{'id':'contact',       'type':'string',  'mode':'w'},
	{'id':'email',         'type':'string',  'mode':'w'},
	{'id':'shiptoaddress', 'type':'text',    'mode':'w'},
        {'id':'shiptophone',   'type':'string',  'mode':'w'},
        {'id':'shiptofax',     'type':'string',  'mode':'w'},
    )

    #__allow_access_to_unprotected_subobjects__ = 1
    
    manage_options = ({'label':'Contents', 'action':'manage_main'},
                      {'label':'Properties', 'action':'manage_propertiesForm',},
                      {'label':'View', 'action':''}) + \
                     BLAttachmentSupport.manage_options

    manage_main = PageTemplateFile('zpt/view_order', globals())

    # debug ...
    manage_btree = BObjectManager.manage_main
    
    def __init__(self, id, title, discount=0.0, taxincluded=0, notes='', shiptoaddress='',
                 contact='', email='', orderdate=DateTime(), reqdate=DateTime() + 7):
        self.id = id
        self.manage_edit(title, orderdate, reqdate, notes, discount,
                         taxincluded, contact, email, shiptoaddress)

    def orderItemValues(self):
        return self.objectValues('BLOrderItem')

    def isBuy(self):
        """
        returns true if this a purchase order
        """
        return self.blLedger().isPayable()

    def isSell(self):
        """
        return true if this is a sales order
        """
        return not self.isBuy()

    def manage_edit(self, title, orderdate, reqdate, notes='', discount=0.0, taxincluded=0, 
	            contact='', email='', shiptoaddress='', items=[], REQUEST=None):
        """ """
        if not isinstance(orderdate, DateTime):
            orderdate = DateTime(orderdate)
        if not isinstance(reqdate, DateTime):
            reqdate = DateTime(reqdate)
        try:
            discount = float(discount)
        except:
            raise ValueError, discount
        if discount > 100.0 or discount < 0.0:
            raise ValueError, discount
	self.title = title
        self.orderdate = orderdate
        self.reqdate = reqdate
        self.taxincluded = bool(taxincluded)
        self.discount = discount / 100.0
        self.notes = notes
        self.contact = contact
        self.email = email
        self.shiptoaddress = shiptoaddress
        self.entered_by = getSecurityManager().getUser().getUserName()
        if items:
            for item in items:
                ob = self._getOb(item.id)
                ob.quantity = item.qty
                try:
                    assert_currency(item.unit)
                    ob.unit = item.unit
                except:
                    ob.unit = ZCurrency(item.unit)
            # if we're called from ctor (without context) we fail ...
            try:
                self.setStatus()
            except AttributeError:
                pass

        if REQUEST is not None:
            return self.manage_main(self, REQUEST)


    def manage_delObjects(self, ids=[], REQUEST=None):
        """
        delete order items and possibly demote status
        """
        if ids:
            BObjectManager.manage_delObjects(self, ids)
            self.setStatus()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def notifyWorkflowCreated(self):
        # hmmm CMFCatalogAware causes our workflow to hang as our first
        # transition is AUTOMATIC ...
        pass

    def setStatus(self):
        """
        does automatic status promotions - as all these functions are private :(
        """
        wftool = getToolByName(self, 'portal_workflow')
        status = self.status()

        if status == 'incomplete':
	    # some orders may contain 'free' items ...
            if self.getGross() > 0 or self.orderItemValues():
                #raise AssertionError, 'doing open transition...'
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.ordering)
        elif status == 'open':
            if not self.orderItemValues():
                wf = wftool.getWorkflowsFor(self)[0]
                wf._executeTransition(self, wf.transitions.incomplete)
	elif status == 'paid':
	    # if its a zero-value order then promote payment to confirmed
	    txn = self.blTransaction()
	    if not txn or txn.creditTotal() == 0:
		wf._executeTransition(self, wf.transitions.confirm)
        self.indexObject(idxs=['status'])

    def all_meta_types(self):
        """
        only allow adding Order Items if status is open, uninvoiced, incomplete
        """
        if self.status() in ('open', 'uninvoiced', 'incomplete'):
            return [ ProductsDictionary('BLOrderItem') ]
        return []

    def getDiscount(self):
        """
        """
        return self.getGross() * self.discount

    def getGross(self):
        """
        return total value of order before deductions
        """
        # this is written to allow for non-commutitivity of ZCurrency ...
        items = self.objectValues('BLOrderItem')

        if items:
            return reduce(operator.add, map(lambda x: x.calculateGrossPrice(), items))

        return self.blAccount().zeroAmount()

    def getTax(self):
        """
        return the total tax(s) levied on this order
        """
        tax = self.blAccount().zeroAmount()
        if not self.taxincluded:
            tax_accts = self.Ledger.accountsForTag('sales_tax')
            if tax_accts:
                tax = reduce(operator.add,
                             map(lambda x: self.calculateTax(x, self.orderdate), tax_accts))
        return tax

    def getNet(self, **kw):
        """
        return net value (plus tax, freight, less discounts etc) of order
        """
        #
        # we are assuming tax rates apply evenly across all items ...
        # this could delegate to calculateTax, but it's more efficient!
        #

        total = self.getGross()
            
        if self.discount:
            total = total * (1.0 - self.discount)

	# add freight charges  -  quietly ignore if blorder_frieght script not found or broken ...
        try:
            freight = self.blorder_freight()
        except:
            freight = 0
            
	if freight > 0:
	    if freight.currency() != total.currency():
	        rate = self.portal_bastionledger.crossBuyRate(total.currency(), freight.currency())
	        freight = ZCurrency(total.currency(), freight.amount() / rate)
	    total += freight

        # calculate tax on amount + freight
        if not self.taxincluded:
            bt = getToolByName(self, 'portal_bastionledger')
            tax = bt.calculateTax(kw.get('effective', DateTime()),
                                  total,
                                  self.aq_parent)
            total += tax

	return total


    def modifiable(self):
        return  self.status() in ('open', 'incomplete',)

    def invoice_date(self):
	"""
	return the date the order was posted to the ledger
	"""
	txn = self.blTransaction()
	if txn:
	    return txn.effective_date
        # hmmm - not posted yet - let's just return None
        return None

    def modificationTime(self):
        """ """
        return self.bobobase_modification_time().strftime('%Y-%m-%d %H:%M')

    def weight(self):
	"""
	return the weight of the order - used to calculate freigh costs etc
	"""
	weight = 0.0
	for item in self.orderItemValues():
	    weight += item.blPart().weight * item.quantity
	return weight

    def calculateTax(self, tax_account=None, effective=None):
        """
        this is to display total tax for a single tax rate ...
        if no tax account is given, use the underlying ledger account
        """
        # TODO - we need to be checking tax codes in the account and tiering
        # against this ...
        tool = getToolByName(self, 'portal_bastionledger')

        # we just need the tax codes on the underlying account ...
        return tool.calculateTax(effective or DateTime(),
                                 self.getGross() * (1.0 - self.discount),
                                 self.blAccount())
        
    def manage_cancel(self, REQUEST=None):
        """
	cancel the order, reversing any transaction  
	"""
	if not self.status() == 'cancelled':
	    status = 'cancelled'
	    txn = self.blTransaction()
            # maybe some dickhead reversed the txn separate to cancelling the order ...
            if txn:
                if txn.status() == 'posted':
                    txn.manage_reverse()
                elif txn.status() != 'reversed':
                    raise PostingError, 'Somebody has screwed with the transaction underlying this order'
            self._status(status)
	
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
            
    def manage_invoice(self, REQUEST=None):
        """
        post an invoice transaction ...
        """
	if not self.status() == 'invoiced':
            self._status('invoiced')
            self.aq_parent.manage_postOrder(self)
                          
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_finish(self, REQUEST=None):
        """
        post an invoice transaction ...
        """
	if not self.status() == 'processed':
            self._status('processed')
                          
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def blTransaction(self):
	"""
	if this order has been posted at any time in it's workflow, it will
	have a txn_id

	Note that if it's a zero-value order, then there will be no transaction...
	"""
	if hasattr(aq_base(self), 'txn_id'):
	    return self.blLedger()._getOb(self.txn_id)
	return None

    def blAccount(self):
        """
        return the underlying ledger account
        """
        # hmmm - overloading functionality for different contexts
        accid = getattr(aq_base(self), '_account', None)
        if accid:
            try:
                return getattr(aq_base(self.aq_parent), accid)
            except AttributeError:
                pass

        return self.aq_parent
            
                         
    def manage_emailInvoice(self, notify_email='', message='',REQUEST=None):
        """
        email invoice to recipient ...
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise
        
        if not notify_email:
            notify_email = self.blAccount().email

        sender = self.blLedger().email
        if not sender:
            if REQUEST:
                REQUEST.set('manage_tabs_message', """Ledger's Correpondence Email unset!""")
                return self.manage_main(self, REQUEST)
            raise LedgerError, """Ledger's Correspondence Email unset!"""

        # ensure 7-bit
        mail_text = str(self.blinvoice_template(self, self.REQUEST, email=notify_email))

        mailhost._send(sender, notify_email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Invoice emailed to %s' % notify_email)
            return self.manage_main(self, REQUEST)

    def blInventory(self):
        ledger = self.blLedger()
        #while not ledger.meta_type in ('BLOrderBook', 'BLCashBook'):
        #    ledger = ledger.aq_parent

        return ledger.aq_parent._getOb(ledger.inventory)
    
    def availableParts(self):
        #
        # TODO: restrict this to only onhand ???
        #
        return map(lambda x: x.getObject(),
                   self.blInventory().catalog(meta_type='BLPart'))

    def _setObject(self, id, object, roles=None, user=None, set_owner=1):
        BObjectManager._setObject(self, id, object, roles, user, set_owner)
        self.setStatus()

    def Xmanage_beforeDelete(self, item, container):
        self.unindexObject()

    def indexObject(self, idxs=[]):
        """ Handle indexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = getattr(self, 'catalog')
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
            cat = getattr(self, 'catalog')
            url = '/'.join(self.getPhysicalPath())
            cat.uncatalog_object(url)
        except:
            pass

    def isOpen(self):
        """ is the order still active """
        return self.status() in ['incomplete', 'open']

    def manage_status_modify(self, workflow_action, REQUEST=None):
        """
        perform the workflow (very Plone ...)
        """
        state = self.content_status_modify(workflow_action=workflow_action)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'State Changed')
            return self.manage_main(self, REQUEST)

    def manage_addOrderItem(self, part, qty=1, unit=0, discount=None, amount=None, REQUEST=None):
        """
        part is an id (or a part)
        """
        id = manage_addBLOrderItem(self, id, qty=qty, unit=unit,discount=discount, amount=amount)
        return id

    def _repair(self):
	if self.__dict__.has_key('status'):
	    status = self.__dict__['status'].lower()
	    if status == 'uninvoiced':
		status = 'open'
	    assert status != 'uninvoiced', status
	    self._status(status)
	    del self.__dict__['status']
	    self._p_changed = 1
        if self.status() == 'uninvoiced':
	    self._status('open')
	if type(self.shiptoaddress) == type([]):
	    self.shiptoaddress = '\n'.join(self.shiptoaddress)
        map( lambda x:x._repair(), self.objectValues('BLOrderItem') )


AccessControl.class_init.InitializeClass(BLOrder)

def addBLCashBook(self, id, title='',REQUEST=None):
    """
    Plone-based entry
    """
    inventory_id = self.bastionLedger().objectIds('BLInventory')[0]

    # lets just guess at the regular bank account ...
    try:
        control = self.Ledger.accountsForTag('bank_account')[0].getId()
    except:
        control = addBLAccount(self.Ledger, id, title)
    return self.manage_addBLCashBook(id, control, inventory_id, 'C', title)


manage_addBLCashBookForm = PageTemplateFile('zpt/add_cashbook', globals()) 
def manage_addBLCashBook(self, id, controlAccount, inventory,
                         prefix='C', title='', REQUEST=None,):
    """ adds an orderbook """
    #if not self.BastionMerchantService:
    #    msg = '''You need a BastionBanking.BastionMerchantService in order to process cash orders.  This is available from http://www.last-bastion.net/BastionBanking.'''
    #    raise AttributeError, msg

    # do some checking ...
    Ledger = self.Ledger
    control = Ledger._getOb(controlAccount)
    assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
    assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."
    
    self._setObject(id, BLCashBook(id, title, control, inventory,
                                   Ledger.currencies or [self.currency], account_prefix=prefix))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

    return id

class BLCashAccount(BLOrderAccount):
    """
    An account where all orders must be paid in advance
    This is a placeholder for polymorphically deciding upon order construction
    """
    meta_type = portal_type = 'BLCashAccount'

    def manage_addOrder(self, title='', orderdate=None, taxincluded=False, discount=0.0, 
                        buysell='buy', REQUEST=None):
        """
        Add an order to the account
        """
        id = self.aq_parent.nextOrderNo()
        self._setObject(id, 
                        BLCashOrder(id, title, 
                                    orderdate=orderdate or DateTime(),
                                    discount=discount,
                                    taxincluded=taxincluded, 
                                    buysell=buysell))
        if REQUEST:
            return REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' % (self.getId(),id) )
        return self._getOb(id)

AccessControl.class_init.InitializeClass(BLCashAccount)

class BLCashOrder(BLOrder):
    """
    An order which doesn't warrant setting up an account.  You may elect to
    perform immediate cash payment too.
    """
    meta_type = portal_type = 'BLCashOrder'

    __allow_access_to_unprotected_subobjects__ = 1
    
    __ac_permissions__ = BLOrder.__ac_permissions__ + (
	(OperateBastionLedgers, ('manage_pay', 'upgradeToAccount',)),
	(OverseeBastionLedgers, ('manage_confirm',)),
	)

    BuySell = ('buy', 'sell')

    buysell = 'buy'

    _properties = BLOrder._properties + (
        {'id':'buysell', 'type':'selection', 'mode':'w', 'select variable':'BuySell'},
        )

    def __init__(self, id, title, discount=0.0, taxincluded=0, notes='', shiptoaddress='',
                 contact='', email='', orderdate=DateTime(), reqdate=DateTime() + 7, buysell='sell'):
        BLOrder.__init__(self, id, title, discount, taxincluded, notes, shiptoaddress,
                         contact, email, orderdate, reqdate)
        self._updateProperty('buysell', buysell)

    def isBuy(self):
        """
        locally decide if we're a buy or sell order
        """
        return self.buysell == 'buy'

    def manage_pay(self, REQUEST=None):
        """
        post the payment against the account (and implicitly the bank account)
        """
        self.manage_postOrder(self)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    #
    # TODO - think about permissions on this - we're kind of expecting a third-party
    # back-end to trigger this - they won't have permissions ...
    #

    def manage_confirm(self, stateobject=None, REQUEST=None):
        """
        confirm that payment has been received - this should be called from
        an after transition, otherwise further processing will stomp over the
        state we're setting
        """
        txn = self.blTransaction()

	# if it's a zero-value order, there will be no txn ...
	if not txn:
	   return

        tstatus = txn.status()

        if tstatus == 'posted':
            # excellent - as you were ...
            return

        #
        # OK - we're going to screw with the workflow engine and return
        # to a prior state without running any transitions (hopefully)
        #
        wftool = getToolByName(self, 'portal_workflow')
        wf = wftool.getWorkflowsFor(self)[0]
        if tstatus == 'complete':
            # still no word from payment service - remain in confirm state (maybe
            # we could promote this to dispatched ...)
            states = stateob.old_state
        elif tstatus == 'rejected':
            states = stateob.new_state
            states['review_state'] = 'open'
        else:
            raise InvalidState, 'confirm received bad transaction state: %s (tid=%s)' % (tstatus, txn.getId())  
        wf._changeStateOf(txn, states)

    def upgradeToAccount(self, orderbook_id):
        """
        take the order details and create an orderaccount in the given orderbook
        """
        orderbook = self.bastionLedger()._getOb(orderbook_id)

        assert isinstance(orderbook, BLOrderBook), 'Not a BLOrderBook: %s' % orderbook

        aid = manage_addBLOrderAccount(orderbook, title=self.contact)
                                       
        account = orderbook._getOb(aid)

        account.manage_changeProperties(contact=self.contact,
                                        address=self.address,
                                        email=self.email,
                                        notes=self.notes,
                                        shiptoaddress=self.shiptoaddress)
        return account

AccessControl.class_init.InitializeClass(BLCashOrder)

class BLCashBook(BLOrderBook):
    """
    This is a repository for cash orders.
    
    The the posting and paying for an order are combined.
    """
    meta_type = portal_type = 'BLCashBook'

    account_types = ('BLCashAccount',)

    implements(ICashBook)

    def __init__(self, id, title, control, inventory, currencies,
                 order_prefix='Q', account_prefix='C', txn_prefix='C' ):
        BLOrderBook.__init__(self, id, title, control, inventory, currencies,
                             order_prefix, account_prefix, txn_prefix )

    def nextAccountId(self):
        raise AssertionError, 'This should be irrelevant!'

    def _delObject(self, id, tp=1, suppress_events=False):
        if id == 'CASH':
            raise BeforeDeleteException, 'Cannot delete CASH account'
        BLCashBook._delObject(id, tp,suppress_events)

    def orderStatuses(self):
        """
        return a list of status ids associated with order workflow
        """
        return getToolByName(self, 'portal_workflow').blcashorder_workflow.states.objectIds()

    def _repair(self):
        #if not getattr(aq_base(self.Processes), 'postOrder', None):
        #    self.isreceivable = None
        #    self._updateProperty('isreceivable', self.controlAccount().type == 'Asset')
        BLOrderBook._repair(self)

AccessControl.class_init.InitializeClass(BLCashBook)


def addOrder(ob, event):
    ob.indexObject()
    # hmmm - acquire notes - if it's a QuoteManager, the field is called 'disclaimer'
    if isinstance(ob.aq_parent, BLOrderAccount):
        notes = ob.aq_parent.notes or ob.aq_parent.aq_parent.instructions
    else:
        notes = getattr(ob.aq_parent, 'disclaimer', '')
    if notes:
        ob._updateProperty('notes', notes)
    # force auto state change ...
    ob.setStatus()

def addCashBook(ob, event):
    # TODO - cash books should be ambiguous but we're making them Asset's ...

    # if it's a copy, then this will fail because we don't allow delete ...
    if not getattr(aq_base(ob), 'CASH', None):
        ob._setObject('CASH',
                      BLCashAccount('CASH', 'Cash Account', '', 'Asset',
                                    ob.defaultCurrency()))

    bt = getToolByName(ob, 'portal_bastionledger')
    if bt.hasTaxTable('sales_tax'):
        account = ob.CASH
        account.manage_addTaxGroup('sales_tax')

