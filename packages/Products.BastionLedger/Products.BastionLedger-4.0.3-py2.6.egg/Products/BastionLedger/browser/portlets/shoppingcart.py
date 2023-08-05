#    Copyright (C) 2008  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import types
from zope import schema
from zope.interface import implements
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlet.static import PloneMessageFactory as _
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName

class IShoppingCartPortlet(IPortletDataProvider):
    """ Shopping cart portlet """

    ledgerid = schema.ASCIILine(title=_(u"Ledger Id"),
                                description=_(u"id of the BastionLedger for the orders."),
                                required=True,
                                default='')

    orderbookid = schema.ASCIILine(title=_(u"Orderbook Id"),
                              description=_(u"id of the Receivables or CashBook for the orders."),
                              required=True,
                              default='')

    accountid = schema.ASCIILine(title=_(u"Account Id"),
                                 description=_(u"id of the order account."),
                                 required=True,
                                 default='CASH')

    cartcookieid = schema.ASCIILine(title=_(u"Cart Cookie Id"),
                              description=_(u"We use a cookie to store the user's cart - you can set it here."),
                              required=True,
                              default='_CartId')

    emptyphrase = schema.TextLine(title=_(u"Empty Phrase"),
                          description=_(u"Message to appear in portlet when cart is empty"),
                          required=True,
                          default=u'Your cart is empty')

    partids = schema.Text(title=_(u"Part Ids"),
                          description=_(u"Id's of all Inventory Parts purchasable via this portlet - leave blank to include everything"),
                          required=False,
                          default=u'')


class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('shoppingcart.pt')

    @property
    def available(self):
        return self.orderaccount() is not None

    def ledger(self):
        return getattr(self.context, self.data.ledgerid, None)

    def orderbook(self):
        ledger = self.ledger()
        if ledger:
            return getattr(ledger, self.data.orderbookid, None)
        return None
    
    def orderaccount(self):
        orderbook = self.orderbook()
        if orderbook:
            return getattr(orderbook, self.data.accountid, None)

    def orderid(self):
        return self.context.blshoppingcart_getId(self.data.cartcookieid)

    def order(self):
        account = self.orderaccount()
        if account:
            orderid = self.orderid()
            if orderid:
                return getattr(orderaccount, orderid, None)
        return None

    def inventory(self):
        orderaccount = self.orderaccount()
        if orderaccount:
            return orderaccount.aq_parent.blInventory()
        return None
    
    def parts(self):
        parts = self.data.partids
        if type(parts) in types.StringTypes:
            parts = parts.split('\n')
        inv = self.inventory()
        if inv:
            if parts:
                return inv.searchObjects(id=parts)
            else:
                return inv.partValues()
        return []

    def emptyphrase(self):
        return self.data.emptyphrase
    
    def site_url(self):
	return getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

class Assignment(base.Assignment):
    """ Assigner for portlet. """
    implements(IShoppingCartPortlet)
    title = _(u'Shopping Cart Portlet')
    
    def __init__(self, ledgerid, orderbookid, accountid, cartcookieid, emptyphrase, partids):
        self.ledgerid = ledgerid
        self.orderbookid = orderbookid
        self.accountid = accountid
        self.cartcookieid = cartcookieid
        self.emptyphrase = emptyphrase
        self.partids = partids

class AddForm(base.AddForm):
    form_fields = form.Fields(IShoppingCartPortlet)
    label = _(u"Add Shopping Cart Portlet")
    description = _(u"This portlet displays shopping cart summaries.")

    def create(self, data):
        return Assignment(ledgerid=data.get('ledgerid', 'ledger'),
                          orderbookid=data.get('orderbookid', 'CashBook'),
                          accountid=data.get('accountid', 'CASH'),
                          cartcookieid=data.get('cartcookieid', '_CartId'),
                          emptyphrase=data.get('emptyphrase', u'Your cart is empty'),
                          partids=data.get('partids', u''))    

class EditForm(base.EditForm):
    form_fields = form.Fields(IShoppingCartPortlet)
    label = _(u"Edit Shopping Cart Portlet")
    description = _(u"This portlet displays shopping cart summaries.")
