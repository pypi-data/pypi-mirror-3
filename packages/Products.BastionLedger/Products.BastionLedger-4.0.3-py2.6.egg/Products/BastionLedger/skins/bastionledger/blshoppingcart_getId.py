## Python Script "blshoppingcart_getId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cartid='_CartId'
##title=query cookies for shopping cart id

# set infinitely unexpiring cookie (payment processing can expire it ...
return context.REQUEST.cookies.get(cartid, '')
