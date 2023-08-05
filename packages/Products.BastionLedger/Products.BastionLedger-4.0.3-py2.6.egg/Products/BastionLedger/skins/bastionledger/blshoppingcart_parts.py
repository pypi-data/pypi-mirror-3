## Python Script "blshoppingcart_parts"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=context sensitive return of shopping cart items from an OrderBook
##
    
# just get them all ...
if getattr(context, 'getInventory', None):
    return context.getInventory().partValues()
