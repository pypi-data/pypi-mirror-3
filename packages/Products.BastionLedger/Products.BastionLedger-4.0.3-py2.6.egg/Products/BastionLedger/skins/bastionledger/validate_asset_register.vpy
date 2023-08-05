## Controlled Python Script "validate_asset_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subtypes=[]
##title=Validates properties of an asset register
##
if not subtypes:
    state.setError('subtypes', 'Asset Subtypes Required', 'subtypes_required')
else:
    valid = context.getSubTypes()
    # hmmm - just report the last one ...
    for st in subtypes:
       if not st in valid:
	  state.setError('subtypes', 'Invalid Subtype: %s' % st, 'subtypes_invalid')


if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

