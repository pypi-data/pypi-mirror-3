## Controller Python Script "blchart_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=chart of account actions
##
REQUEST=context.REQUEST

if REQUEST.has_key('form.button.Delete'):
    bad = []
    for id in REQUEST['ids']:
        account = getattr(context, id, None)
        if account:
            if len(account.entryValues()) == 0:
	        context.manage_delObjects([id])
            else:
                bad.append(account.accno)
    if bad:
        context.plone_utils.addPortalMessage('Account(s) have entries: %s' % ', '.join(bad))
    else:
        context.plone_utils.addPortalMessage('Deleted account(s)')

return state

