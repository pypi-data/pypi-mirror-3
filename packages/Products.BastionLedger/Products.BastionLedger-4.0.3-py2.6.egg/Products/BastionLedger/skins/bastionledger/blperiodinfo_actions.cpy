## Controller Python Script "blperiodinfo_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=balances=[],ids=[]
##title=edit period-end figues etc
##
request=context.REQUEST

if request.has_key('form.button.Save'):
    context.manage_updateReportingBalances(balances)
elif request.has_key('form.button.Recalculate'):
    context.manage_recompute()
    context.plone_utils.addPortalMessage('Recalculated Year end')
elif request.has_key('form.button.Delete'):
     context.manage_delete(ids)
elif request.has_key('form.button.Reverse'):
     context.manage_reverse(ids)

return state

