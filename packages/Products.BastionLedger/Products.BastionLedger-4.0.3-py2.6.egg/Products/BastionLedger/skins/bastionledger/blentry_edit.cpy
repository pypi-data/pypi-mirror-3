## Controller Python Script "blentry_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='',amount=None,posting_amount=None
##title=edit a transaction
##
REQUEST=context.REQUEST

from Products.BastionLedger.utils import assert_currency

#
# you can only edit amount in unposted transactions ...
#
if amount:
   try:
       assert_currency(amount)
   except:
       state.setError('amount', 'Invalid Amount', 'invalid_amount')
       context.plone_utils.addPortalMessage('Please correct indicated errors', 'error')
       return state.set(status='failure') 
        
if getattr(context, 'posted_amount', None):
   try:
       assert_currency(posting_amount)
   except:
       state.setError('posted_amount', 'Invalid Amount', 'invalid_amount')
       context.plone_utils.addPortalMessage('Please correct indicated errors', 'error')
       return state.set(status='failure') 
   
   context.edit(title, amount, posting_amount)
else:
   context.edit(title, amount)

context.plone_utils.addPortalMessage('Updated Entry')
return state

