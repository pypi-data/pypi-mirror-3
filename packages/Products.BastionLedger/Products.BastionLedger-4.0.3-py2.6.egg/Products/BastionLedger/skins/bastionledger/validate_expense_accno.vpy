## Controlled Python Script "validate_expense_accno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=expense_accno=''
##title=Validates shipping instructions
##
if not expense_accno:
    state.setError('expense_accno', 'Account Number Required', 'accno_required')

if not expense_accno in map(lambda x: x.getId(), self.Ledger.Accounts(tags='part_cogs')):
    state.setError('expense_accno', 'Invalid Expense Account', 'invalid_expense_accno')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

