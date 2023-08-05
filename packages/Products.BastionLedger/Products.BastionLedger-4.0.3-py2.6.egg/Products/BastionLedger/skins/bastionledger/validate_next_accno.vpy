## Controlled Python Script "validate_next_accno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=account_id=''
##title=Validates next account number 
##
if not account_id:
    state.setError('next_accno', 'Account Number Required', 'accno_required')
else:
    try:			
        i = int(account_id)
    except:	
        state.setError('next_accno', 'Invalid Account Number (NAN)', 'invalid_accno')


if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

