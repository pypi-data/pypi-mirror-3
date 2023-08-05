## Controller Python Script "blforecaster_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', description='', account_ids=[], id=''
##title=edit forecaster properties
##
REQUEST=context.REQUEST

if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.edit(title, description, account_ids)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Asset Register %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

