## Controller Python Script "blledger_change_controlAccount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=controlAccount='',effective=None
##title=change the control account for a subsidiary ledger
##

if not controlAccount:
    state.setError('controlAccount', 'Account Number Required', 'accno_required')

if not controlAccount in context.Ledger.accountIds():
    state.setError('controlAccount', 'Unknown Account Number', 'accno_unknown')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')

context.manage_changeControl(controlAccount, effective or DateTime())

context.plone_utils.addPortalMessage('Control Account Changed')
return state

