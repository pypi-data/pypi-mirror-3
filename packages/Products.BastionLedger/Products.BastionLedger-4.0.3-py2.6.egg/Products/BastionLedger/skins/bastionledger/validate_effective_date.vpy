## Controlled Python Script "validate_effective_date"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective=''
##title=Validates shipping instructions
##
from DateTime import DateTime

if not effective:
    state.setError('effective', 'Effective Date Required', 'effective_date_required')

if not isinstance(effective, DateTime):
    try:
        effective = DateTime(effective)
    except:
        state.setError('effective', 'Invalid Effective Date', 'invalid_effective_date')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

