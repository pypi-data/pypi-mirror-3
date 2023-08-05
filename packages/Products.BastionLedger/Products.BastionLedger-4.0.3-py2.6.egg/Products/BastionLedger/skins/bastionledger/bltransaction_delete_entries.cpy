## Controller Python Script "bltransaction_delete_entries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=delete entries from a transaction
##

if context.modifiable():

    if context.status() in ('posted',):
        context.manage_unpost()

    id = context.getId()
    new_context = context.portal_factory.doCreate(context, id)

    if ids:
        new_context.manage_delObjects(ids)

    new_context.plone_utils.addPortalMessage('Deleted entries')


return state.set(context=new_context)

