## Controlled Python Script "validate_next_txnno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=txn_id=''
##title=Validates next transaction number 
##
if not txn_id:
    state.setError('next_txnno', 'Transaction Number Required', 'txnno_required')
else:
    try:
        i = int(txn_id)
    except:
        state.setError('next_txnno', 'Invalid Transaction Number (NAN)', 'invalid_txnno')


if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

