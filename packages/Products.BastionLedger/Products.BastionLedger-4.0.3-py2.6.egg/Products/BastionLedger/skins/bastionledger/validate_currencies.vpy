## Controlled Python Script "validate_currencies"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=currencies=[]
##title=Validates currencies
##
if not currencies:
    state.setError('currencies', 'Currencies Required', 'currencies_required')
else:    
    available_currencies = context.allCurrencies()
    for cur in currencies:
        if cur not in available_currencies:
            state.setError('currencies', 'Unknown/Untraded currency: %s' % cur, 'unknown_currency')
            break

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

