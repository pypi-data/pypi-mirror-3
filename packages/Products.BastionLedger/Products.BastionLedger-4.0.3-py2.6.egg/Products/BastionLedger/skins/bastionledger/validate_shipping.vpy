## Controlled Python Script "validate_shipping"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=shiptoaddress='',contact=''
##title=Validates shipping instructions
##
if not shiptoaddress:
    state.setError('shiptoaddress', 'Invalid Shipping Address', 'invalid_shiptoaddress')

if not contact:
    state.setError('contact', 'Invalid Shipping Contact Name', 'invalid_shiptocontact')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

