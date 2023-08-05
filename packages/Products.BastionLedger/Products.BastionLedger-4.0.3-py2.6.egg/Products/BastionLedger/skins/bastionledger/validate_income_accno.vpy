## Controlled Python Script "validate_income_accno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=income_accno=''
##title=Validates shipping instructions
##
if not income_accno:
    state.setError('income_accno', 'Account Number Required', 'accno_required')

if not income_accno in map(lambda x: x.getId(), self.Ledger.Accounts(tags='part_inc')):
    state.setError('income_accno', 'Invalid Income Account', 'invalid_income_accno')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

