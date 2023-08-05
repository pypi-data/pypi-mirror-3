##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective,amount,reference=''
##title=do a payment on account
##
from Products.CMFCore.utils import getToolByName
from Products.BastionBanking import ZReturnCode
from Products.BastionLedger.BLSubsidiaryTransaction import manage_addBLSubsidiaryTransaction
from Products.BastionLedger.BLEntry import manage_addBLEntry
from Products.BastionLedger.BLSubsidiaryEntry import manage_addBLSubsidiaryEntry

# acquire the GL
ledger = context.Ledger
bms = context.getBastionMerchantService()

if bms:
    bank_account = ledger.accountsForTag('merchant')[0]
else:
    bank_account = ledger.accountsForTag('bank_account')[0]

#
# go create our Payment transaction
#
payment_id = manage_addBLSubsidiaryTransaction(context.ledger(), 
                                               title='Payment - Thank You',
                                               effective=effective,
                                               ref=reference)
payment_txn = getattr(context, payment_id)
manage_addBLEntry(payment_txn, bank_account, amount)
manage_addBLSubsidiaryEntry(payment_txn, context, -amount)

#
# let the Merchant Service pay and post the txn (if successfully paid)
#
if bms:
    # we presently still need to complete via the BMS return url :(
    #bms.manage_payTransaction(payment_txn, reference, return_url=context.absolute_url())
    bms.manage_payTransaction(payment_txn, reference)
else:
    payment_txn.manage_post()

context.plone_utils.addPortalMessage('Thank you for your payment')
state.set(context=context)

return state
