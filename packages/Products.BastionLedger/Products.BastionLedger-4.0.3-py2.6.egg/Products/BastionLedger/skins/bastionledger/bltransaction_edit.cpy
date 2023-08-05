## Controller Python Script "bltransaction_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective,title='',description=''
##title=edit a transaction
##
REQUEST=context.REQUEST
id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.editProperties(title, description, effective)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited transaction %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

new_context.plone_utils.addPortalMessage('Updated Transaction')

return state.set(context=new_context)

