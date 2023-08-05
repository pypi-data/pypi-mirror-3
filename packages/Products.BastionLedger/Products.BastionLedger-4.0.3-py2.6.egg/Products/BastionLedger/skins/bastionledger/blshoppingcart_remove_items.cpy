## Controller Python Script "blshoppingcart_remove_items"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[],account_id=''
##title=add parts to shopping cart
##
REQUEST=context.REQUEST

#
# we're making some assumptions here about which ledger to find the account in ...
#
if account_id:
    account = getattr(context.bastion_ledger.Receivables, account_id)
else:
    account = context.ledger.CashBook.CASH

order = getattr(account, context.blshoppingcart_getId())
order.manage_delObjects(ids)

#
# why don't metadata [action] tags work ???
# 
REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
