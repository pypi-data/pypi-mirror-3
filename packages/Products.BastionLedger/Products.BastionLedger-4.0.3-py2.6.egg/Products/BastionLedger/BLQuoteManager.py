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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import access_contents_information
from Products.CMFCore import permissions
from OFS.PropertyManager import PropertyManager
from DateTime import DateTime
from Products.ZCatalog.ZCatalog import ZCatalog

from Products.BastionBanking.ZCurrency import ZCurrency, CURRENCIES

from BLBase import *
from Permissions import OperateBastionLedgers, OverseeBastionLedgers, ManageBastionLedgers
from BLOrderBook import BLOrderBook, BLOrder, manage_addBLOrderAccount, manage_addBLOrder
from BLAttachmentSupport import BLAttachmentSupport
from BLTaxCodeSupport import BLTaxCodeSupport
from Exceptions import LedgerError

from zope.interface import Interface, implements

from interfaces.tools import IBLLedgerToolMultiple


manage_addBLQuoteManagerForm = PageTemplateFile('zpt/add_quotemgr', globals())
def manage_addBLQuoteManager(self, id, title='', REQUEST=None):
    """
    """
    ledger = self.this()
    currency = getattr(ledger, 'currency', 'USD')
    self._setObject(id, BLQuoteManager(id, 
                                       title, 
                                       currency=currency,
                                       orderbooks=ledger.objectIds('BLOrderBook')))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])
    return id

manage_addBLQuoteForm = PageTemplateFile('zpt/add_quote', globals())
def manage_addBLQuote(self, id='', title='', REQUEST=None):
    """
    """
    if not id:
        id = self.generateUniqueId()
    self._setObject(id, BLQuote(id, title))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id

class IQuote(Interface): pass
class IQuoteManager(Interface): pass

class BLQuoteManager(BObjectManagerTree, ZCatalog, BLTaxCodeSupport):
    """
    A tool to manage job quotations

    Optionally include price policy support for markup computations
    """
    meta_type = portal_type = 'BLQuoteManager'

    implements(IQuoteManager, IBLLedgerToolMultiple)

    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (access_contents_information, ('orderbookIds', 'orderbookValues', 
                                       'availableParts', 'blInventory', 
                                       'currencies', 'searchObjects')),
        (ManageBastionLedgers, ('edit',)),
        ) + ZCatalog.__ac_permissions__

    _properties = BObjectManagerTree._properties + (
        {'id':'base_currency', 'type':'selection',        'mode':'w',
         'select_variable':'currencies'},
        {'id':'email',         'type':'string',           'mode':'w'},
        {'id':'orderbooks',  'type':'multiple selection', 'mode':'w',
         'select_variable':'orderbookIds'},
        {'id':'disclaimer',  'type':'text',               'mode':'w'},
        {'id':'expiry_days', 'type':'int',                'mode':'w'},
        )

    manage_options = (
        ZCatalog.manage_options[0],
        {'label':'View', 'action':''},
        {'label':'Tax Codes', 'action':'manage_taxcodes'},
        ) + ZCatalog.manage_options[1:]

    def __init__(self, id, title='', orderbooks=[], disclaimer='', expiry_days=30,
                 currency='USD', email=''):
        ZCatalog.__init__(self, id)
        BObjectManagerTree.__init__(self, id, title)
        self.addIndex('state', 'FieldIndex')
        self.addIndex('Creator', 'FieldIndex')
        self.addColumn('meta_type')
        self.orderbooks = orderbooks
        self.disclaimer = disclaimer
        self.expiry_days = expiry_days
        self.base_currency = currency
        self.email = email

    def all_meta_types(self):
        """
        """
        return [ ProductsDictionary('BLQuote') ]

    def edit(self, orderbooks, disclaimer, expiry_days, base_currency, email):
        """
        """
        self._updateProperty('orderbooks', orderbooks)
        self._updateProperty('disclaimer', disclaimer)
        self._updateProperty('expiry_days', expiry_days)
        self._updateProperty('base_currency', base_currency)
        self._updateProperty('email', email)

    def orderbookIds(self):
        """
        return a list of available order books from which inventories and
        accounts may be raised against
        """
        return map(lambda x: x.getId(),
                   filter(lambda x: isinstance(x, BLOrderBook),
                          self.aq_parent.objectValues()))

    def orderbookValues(self):
        """
        return the orderbooks assigned to this quote manager
        """
        return map(lambda x: self.aq_parent._getOb(x), self.orderbookIds())

    def availableParts(self):
        """
        return all of the available components from the stores associated with
        this quote manager
        """
        inventory = self.blInventory()
        if inventory:
            return inventory.partValues()
        return []

    def blInventory(self):
        """
        hmmm - adding order items presently requires a single inventory, which
        is a complete PITA ...
        """
        inventories = []
        for orderbook in self.orderbookValues():
            inventory = orderbook.blInventory()
            if inventory not in inventories:
                inventories.append(inventory)
        
        if inventories:
            return inventories[0]
        return None

    def currencies(self):
        return CURRENCIES

    def searchObjects(self, REQUEST=None, *args, **kw):
        """
        """
        return map(lambda x: x.getObject(),
                   self.searchResults(REQUEST=REQUEST))

    # BLTaxTableSupport ...
    prettyTitle = BObjectManagerTree.title_or_id

AccessControl.class_init.InitializeClass(BLQuoteManager)

class BLQuote(BLOrder):
    """
    A job quote, containing additional costing info, and promotable
    to an account/order

    There is also basic scheduling info available to contemplate forward workloads

    Maybe Quote's should conform to the Event API ...
    """
    meta_type = portal_type = 'BLQuote'

    implements(IQuote)

    __ac_permissions__ = BLOrder.__ac_permissions__ + (
        (access_contents_information, ('view', 'availableParts', 'blInventory', 
                                       'blOrderBook', 'blAccount', 'blOrder')),
        (OperateBastionLedgers, ('manage_edit', 'manage_send', 
                                 'manage_createAccount', 'manage_raiseOrder', 
                                 'setStatus',)),
        )

    _properties = BLOrder._properties + (
        {'id':'accno',          'type':'string', 'mode':'w'},
        {'id':'orderno',        'type':'string', 'mode':'w'},
        {'id':'company',        'type':'string', 'mode':'w'},
        {'id':'phone',          'type':'string', 'mode':'w'},
        {'id':'est_start_date', 'type':'date',   'mode':'w'},
        {'id':'est_end_date',   'type':'date',   'mode':'w'},
        {'id':'est_days',       'type':'int',    'mode':'w'},
        {'id':'markup_policy',  'type':'string', 'mode':'w'},
    )

    manage_main = PageTemplateFile('zpt/view_quote', globals())

    def __init__(self, id, title, discount=0.0, taxincluded=0, notes='', shiptoaddress='',
                 contact='', email='', orderdate=DateTime(), reqdate=DateTime() + 7):
        BLOrder.__init__(self, id, title, discount, taxincluded, notes, shiptoaddress,
                         contact, email, orderdate, reqdate)
        self.accno = ''
        self.orderno = ''
        self.phone = ''
        self.company = ''
        # job/assignment control info for resource planning???
        self.est_start_date = self.est_end_date = self.orderdate
        self.est_days = 0
        self.markup_policy = ''

    def all_meta_types(self, user=None):
        """
        only allow adding Order Items if status is pending
        """
        if self.status() in ('pending',):
            return [ ProductsDictionary('BLOrderItem') ]
        return []

    def manage_edit(self, title, orderdate, reqdate, notes=[],
                    discount=0.0, taxincluded=0, contact='',
                    email='', shiptoaddress='', items=[],
                    company='', phone='', REQUEST=None):
        """ """
        self._updateProperty('company', company)
        self._updateProperty('phone', phone)
        BLOrder.manage_edit(self, title, orderdate, reqdate, notes,
                            discount, taxincluded, contact, email,
                            shiptoaddress, items)

    def manage_send(self, email='', message='', REQUEST=None):
        """
        send the quotation to the contact
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise
        
        if not email:
            email = self.email

        sender = self.aq_parent.email
        if not sender:
            if REQUEST:
                REQUEST.set('manage_tabs_message', """Ledger's Correpondence Email unset!""")
                return self.manage_main(self, REQUEST)
            raise LedgerError, """Ledger's Correspondence Email unset!"""
                
        # ensure 7bit
        mail_text = str(self.blquote_template(self, self.REQUEST, email=email))

        mailhost._send(sender, email, mail_text)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Quote emailed to %s' % email)
            return self.manage_main(self, REQUEST)

    def manage_createAccount(self, orderbook_id):
        """
        create a BLOrderAccount in the orderbook specified by the id
        """
        orderbook = self.aq_parent.aq_parent._getOb(orderbook_id)
        accno = manage_addBLOrderAccount(orderbook,
                                         title = self.company or self.title,
                                         description = self.description,
                                         currency = self.aq_parent.base_currency)
        account = orderbook._getOb(accno)

        # hmmm - there's a bug in the creditlimit type ..
        account.manage_oaEdit(self.company or self.title, self.description,
                              self.email, self.contact, '', self.phone, '',
                              creditlimit = ZCurrency(self.aq_parent.base_currency, 0))

        self._updateProperty('accno', accno)
        return account

    def manage_raiseOrder(self, orderbook_id=None):
        """
        create an Account if doesn't exist, and raise an order
        """
        account = self.blAccount()
        if not account:
            if not orderbook_id:
                raise AttributeError, 'orderbook_id is required'
            account = self.manage_createAccount(orderbook_id)

        order_id = manage_addBLOrder(account, title=self.title)
        order = account._getOb(order_id)

        order.manage_edit(self.title, DateTime(), DateTime()+ 7,
                          contact = self.contact,
                          email = self.email,
                          discount = self.discount,
                          taxincluded = self.taxincluded)

        for k,v in self.objectItems('BLOrderItem'):
            order._setObject(k, v._getCopy(v))
        order.setStatus()

        self._updateProperty('orderno', order_id)

        return order

    def firstname(self):
        """
        return the first name of the contact person
        """
        if self.contact.find(' ') != -1:
            return self.contact.split(' ')[0]
        return self.contact

    def availableParts(self):
        """
        return all of the available components from the stores associated with
        this quote manager - we need to override our base class
        """
        return self.aq_parent.availableParts()

    def blInventory(self):
        """
        part add/delete needs this
        """
        return self.aq_parent.blInventory()

    def blOrderBook(self):
        """ return the default orderbook """
        orderbooks = self.aq_parent.orderbookValues()
        assert orderbooks, 'Doh - please set up an orderbook in the Quote Manager'
        return orderbooks[0]

    # needed for OrderBook OrderItem adding 
    blLedger = blOrderBook

    def setStatus(self):
        pass


    def blAccount(self):
        """
        returns the underlying order account - if set up
        """
        if self.accno:
            return self.blOrderBook()._getOb(self.accno)
        # not set up, we're probably doing tax calculations, return parent which
        # has tax codes set up
        return self.aq_parent

    def blOrder(self):
        """
        returns the underlying order - if we got that far ...
        """
        if self.orderno:
            return self.blAccount()._getOb(self.orderno)

    def indexObject(self):
        """ Handle indexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = self.aq_parent
            url = '/'.join(self.getPhysicalPath())
            cat.catalog_object(self, url)
        except:
            pass
        
    def unindexObject(self):
        """ Handle unindexing """
        try:
            #
            # just making sure we can use this class in a non-catalog aware situation...
            #
            cat = self.aq_parent
            url = '/'.join(self.getPhysicalPath())
            cat.uncatalog_object(url)
        except:
            pass

    def reindexObject(self, idxs=[]):
        self.unindexObject()
        self.indexObject()


AccessControl.class_init.InitializeClass(BLQuote)




def addQuote(ob, event):
    ob.indexObject()
    # hmmm - acquire notes
    if not ob.notes:
        notes = ob.aq_parent.disclaimer
        if notes:
            ob._updateProperty('notes', notes)


