## Controller Python Script "blquote_raise_order"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderbook=''
##title=raise an order for this quote
##

order = context.manage_raiseOrder(orderbook)

context.plone_utils.addPortalMessage('Order raised')
return state
