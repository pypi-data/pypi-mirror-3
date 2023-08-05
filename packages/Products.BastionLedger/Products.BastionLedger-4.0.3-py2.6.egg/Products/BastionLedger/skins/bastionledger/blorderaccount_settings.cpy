## Controller Python Script "blorderaccount_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=creditlimit,discount,terms,taxincluded=0,notes=[]
##title=operations editable properties
##
REQUEST=context.REQUEST
 
context.manage_oaEdit(context.title, context.description, context.email, context.contact, context.address,
                      context.phone, context.fax, discount, creditlimit, terms, notes, 
                      context.shiptoname, context.shiptoaddress, context.shiptocontact, 
		      context.shiptophone, context.shiptofax, context.shiptoemail,
                      taxincluded)

context.plone_utils.addPortalMessage('Settings Updated')
return state

