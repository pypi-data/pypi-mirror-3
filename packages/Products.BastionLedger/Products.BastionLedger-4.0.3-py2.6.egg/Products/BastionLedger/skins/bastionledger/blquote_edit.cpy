## Controller Python Script "blquote_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderdate,reqdate,taxincluded=0,discount=0.0,notes='',parts=[],title='',contact='',email='',company='',phone='',id=''
##title=edit job quotation
##

if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.manage_edit(title, orderdate,reqdate, notes, discount, taxincluded, 
                        contact, email, context.shiptoaddress, company=company,
                        phone=phone)

for part in parts:
   orderitem = getattr(new_context, part['id'])
   orderitem.manage_edit(orderitem.title, part['quantity'], discount, part['unit'], None, part['note'])

# auto upgrade/downgrade status
new_context.setStatus()

context.plone_utils.addPortalMessage('Edited')

return state.set(context=new_context)
