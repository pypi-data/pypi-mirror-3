## Controller Python Script "bltransactions_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=transactions actions
##
REQUEST=context.REQUEST

if REQUEST.has_key('form.button.Delete'):
    context.manage_delObjects(REQUEST['ids'])
    context.plone_utils.addPortalMessage('Deleted transaction(s)')
elif REQUEST.has_key('form.button.Post'):
    context.manage_postObjects(REQUEST['ids'])
    context.plone_utils.addPortalMessage('Posted transaction(s)')
elif REQUEST.has_key('form.button.Reverse'):
    context.manage_reverse(REQUEST['ids'])
    context.plone_utils.addPortalMessage('Reversed transaction(s)')

return state

