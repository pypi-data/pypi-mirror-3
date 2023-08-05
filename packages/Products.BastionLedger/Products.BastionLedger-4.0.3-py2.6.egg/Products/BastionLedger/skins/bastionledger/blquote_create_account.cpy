## Controller Python Script "blquote_create_account"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderbook
##title=create an orderbook account 
##

account = context.manage_createAccount(orderbook)
context.plone_utils.addPortalMessage('Account Created')

return state
