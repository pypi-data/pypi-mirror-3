## Controller Python Script "bltransaction_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=edit a transaction
##

if context.modifiable():

    if context.status() in ('posted',):
        context.manage_unpost()

    id = context.getId()
    new_context = context.portal_factory.doCreate(context, id)

    if ids:
        new_context.manage_toggle(ids)

    context.plone_utils.addPortalMessage('Toggled Entries')

return state.set(context=new_context)

