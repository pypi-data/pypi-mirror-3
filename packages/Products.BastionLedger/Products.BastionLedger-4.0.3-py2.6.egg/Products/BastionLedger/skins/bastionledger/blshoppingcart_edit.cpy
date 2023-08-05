## Controller Python Script "blshoppingcart_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=contact,email,shiptoaddress
##title=edit shopping cart attributes
##

context.manage_edit(context.orderdate, context.reqdate, context.discount,
                    context.notes , context.taxincluded, contact, email,
                    shiptoaddress)

return state
