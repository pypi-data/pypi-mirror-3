## Controller Python Script "blshoppingcart_add_items"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=part_ids,order_id='',account_id=''
##title=add parts to shopping cart
##
REQUEST=context.REQUEST

#
# we're making some assumptions here about which ledger to find the account in ...
#
if account_id:
    account = getattr(context.bastion_ledger.blLedger().Receivables, account_id)
else:
    account = context.bastion_ledger.blLedger().objectValues('BLCashBook')[0].CASH

if order_id == '':
    order_id = context.blshoppingcart_getId()

if order_id:
    order = getattr(account, order_id)
else:
    order = account.manage_addOrder()
    # this works in conjunction with getShoppingCartId to allow you 
    # to define shopping cart policies
    context.blshoppingcart_setId(order.getId())

for part_id in part_ids:
    item = order.manage_addProduct['BastionLedger'].manage_addBLOrderItem(part_id)
    ref = REQUEST.get('reference', '')
    if ref:
	item.setReference(ref)

#
# why don't metadata [action] tags work ???
# 
REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
