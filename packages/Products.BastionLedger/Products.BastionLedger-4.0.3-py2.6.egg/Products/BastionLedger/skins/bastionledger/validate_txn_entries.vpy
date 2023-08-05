## Controlled Python Script "validate_txn_entries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=addentries=[],editentries=[]
##title=Validates entries being assigned to a transaction
##
from Products.BastionBanking.ZCurrency import ZCurrency

ledger_ids = context.Ledger.accountIds()
if context.meta_type == 'BLSubsidiaryTransaction':
    subsidiary_ids = context.aq_parent.accountIds()

# don't do entries with blank amounts ...
for entries, errortag in ((addentries, 'addentries'),):
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        # verify we can coerce any currency later ...
        if not isinstance(entry.amount, ZCurrency):
            try:
                amt = ZCurrency(entry.amount)
            except:
                state.setError(errortag, 'Invalid currency: %s' % entry.amount, 'invalid_amount')
	        break

        if getattr(entry, 'subsidiary', False):
            if entry.account not in subsidiary_ids:
                state.setError(errortag, 'Invalid Subsidiary Account: %s' % entry.account, 'invalid_subsidiary_account')
                break
        elif entry.account not in ledger_ids:
            state.setError(errortag, 'Invalid Account: %s' % entry.account, 'invalid_account')
            break


if state.getErrors():
    return state.set(status='failure')
else:
    return state

