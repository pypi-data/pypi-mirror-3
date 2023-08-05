## Controller Python Script "blinventory_dispatch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[], 
##title=perform inventory dispatch action
##
REQUEST=context.REQUEST

if REQUEST.has_key('form.button.Cancel'):
    context.dispatcher.manage_cancel(ids)
elif REQUEST.has_key('form.button.Dispatch'):
    context.dispatcher.manage_dispatch(ids)
else:
    raise AssertionError, 'invalid method'
context.plone_utils.addPortalMessage('Properties Updated')
return state

