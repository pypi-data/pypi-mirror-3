## Controller Python Script "blledger_props"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,account_prefix, account_id, txn_prefix, txn_id, currencies, email, description='', instructions='', id=''
##title=edit ledger properties
##

REQUEST=context.REQUEST

if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.manage_edit(title, description, txn_id, account_id, account_prefix, txn_prefix,
                        currencies, email)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Ledger %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

