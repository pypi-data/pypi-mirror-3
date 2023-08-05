## Controller Python Script "blprocess_run"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=run a process
##
REQUEST=context.REQUEST
 
kw = {}

for param in context.parameterMap:
    if REQUEST.has_key(param['id']):
        kw[param['id']] = REQUEST[param['id']]

context.manage_run(**kw)

context.plone_utils.addPortalMessage('Process completed')

return state
