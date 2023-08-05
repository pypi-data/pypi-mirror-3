## Controller Python Script "blorder_additems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=part_ids=[],id=''
##title=add BLOrderItem's
##
REQUEST=context.REQUEST

id = id or context.getId()
new_context = context.portal_factory.doCreate(context, id)

for part_id in part_ids:
    new_context.manage_addProduct['BastionLedger'].manage_addBLOrderItem(part_id)

new_context.blorder_edit(orderdate=REQUEST['orderdate'],
			 reqdate=REQUEST['reqdate'],
                         taxincluded=REQUEST.get('taxincluded', False),
                         discount=REQUEST.get('discount', 0.0),
                         notes=REQUEST['notes'],
                         title=REQUEST['title'],
                         contact=REQUEST['contact'],
                         email=REQUEST['email'],)

return state.set(context=new_context)

