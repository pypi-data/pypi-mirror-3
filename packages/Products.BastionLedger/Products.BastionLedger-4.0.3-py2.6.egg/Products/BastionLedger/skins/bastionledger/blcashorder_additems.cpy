##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=part_ids, buysell, id=''
##title=add BLOrderItem's
##
REQUEST=context.REQUEST

id = id or context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.manage_changeProperties(buysell=buysell)

for part_id in part_ids:
    new_context.manage_addProduct['BastionLedger'].manage_addBLOrderItem(part_id)

context.plone_utils.addPortalMessage('Added Items')
return state.set(context=new_context)
