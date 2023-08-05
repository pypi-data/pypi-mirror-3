## Controller Python Script "blorderaccount_details"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,email,description='',contact='',address='',phone='',fax='',shiptoname='',shiptoaddress='',shiptocontact='',shiptophone='',shiptofax='',shiptoemail=''
##title=customer editable properties
##
REQUEST=context.REQUEST
 
id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.manage_oaEdit(title,description, email, contact, address,  phone, fax, context.discount, 
                          context.creditlimit, context.terms, context.notes, shiptoname, 
                          shiptoaddress, shiptocontact, shiptophone, shiptofax, shiptoemail,
                          context.taxincluded)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

