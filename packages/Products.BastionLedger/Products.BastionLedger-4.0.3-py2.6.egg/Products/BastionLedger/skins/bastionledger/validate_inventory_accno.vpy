## Controlled Python Script "validate_inventory_accno"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=inventory_accno=''
##title=Validates shipping instructions
##
if not inventory_accno:
    state.setError('inventory_accno', 'Account Number Required', 'accno_required')

if not inventory_accno in map(lambda x: x.getId(), self.Ledger.Accounts(tags='part_inv')):
    state.setError('inventory_accno', 'Invalid Inventory Account', 'invalid_inventory_accno')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

