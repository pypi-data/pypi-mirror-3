## Controller Python Script "shoppingcart_deleteitems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids
##title=remove BLOrderItem's
##
context.manage_delObjects(ids)

return state.set()

