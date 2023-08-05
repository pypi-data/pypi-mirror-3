## Controller Python Script "blaccount_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids,delete=False
##title=account actions
##
REQUEST=context.REQUEST

if REQUEST.has_key('form.button.Merge'):
    context.manage_merge(ids, delete)

    context.plone_utils.addPortalMessage('Merged account(s)')

return state

