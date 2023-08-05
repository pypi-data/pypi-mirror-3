## Controller Python Script "bltransactions_bulkload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=accno, currency, entries, post=True
##title=bulk-load entries into txn's against account
##
from Products.BastionBanking.ZCurrency import ZCurrency

#
# verify main form fields
#
try:
    account = context.accountValues(accno=accno)[0]
except:
    state.setError('accno', 'Account not found', 'not_found')
    return state.set(status='failure')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')


parsed_entries = []

#
# parse all the inputs, returning error(s) as discovered
#
for entry in entries:
    effective = entry['effective']

    # empty form fields ...
    if not effective:
        continue

    if len(effective) != 10:
        effective = '%s/%s/%s' % (effective[0:4], effective[4:6], effective[6:8])

    try:
        effective = DateTime(effective)
    except Exception, e:
        context.plone_utils.addPortalMessage('Effective Date Error: %s' % str(e), 'error')
        return state.set(status='failure')

    try:
        other = context.accountValues(accno=entry['accno'])[0]
    except Exception, e:
        context.plone_utils.addPortalMessage('Account not found: %s' % entry['accno'], 'error')
        return state.set(status='failure')

    try:
        amount = ZCurrency('%s %s' % (currency, entry['amount']))
    except Exception, e:
        context.plone_utils.addPortalMessage('Invalid currency: %s %s' % (currency, entry['amount']), 'error')
        return state.set(status='failure')

    parsed_entries.append((entry['description'], effective, amount, other))

#
# we're good to go, create the transactions
#
count = 0

for entry in parsed_entries:
    txn = account.createTransaction(effective=entry[1], title=entry[0])
    account.createEntry(txn, -entry[2])
    entry[3].createEntry(txn, entry[2])

    count += 1

    if post:
        txn.manage_post()


context.plone_utils.addPortalMessage('Posted %i transactions' % count)
return state

