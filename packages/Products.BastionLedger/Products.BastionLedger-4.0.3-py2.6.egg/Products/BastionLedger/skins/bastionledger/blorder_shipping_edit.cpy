## Controller Python Script "blorder_shipping_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=contact, email, shiptoaddress, shiptophone='', shiptofax=''
##title=edit shipping instructions
##

context.manage_changeProperties(contact=contact, 
                                email=email, 
                                shiptoaddress=shiptoaddress,
				shiptophone=shiptophone,
				shiptofax=shiptofax)

# auto upgrade/downgrade status
context.setStatus()

context.plone_utils.addPortalMessage('Updated shipping details')

return state