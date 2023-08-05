## Controller Python Script "blallocation_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=quantity, definition,issue_date=None,percentage_paid=100.0, id=''
##title=edit a shareholders share allocation
##
REQUEST=context.REQUEST

if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)
new_context.editProperties(quantity, definition, issue_date or DateTime(), percentage_paid)        
new_context.plone_utils.addPortalMessage('Updated Allocation')

return state.set(context=new_context)

