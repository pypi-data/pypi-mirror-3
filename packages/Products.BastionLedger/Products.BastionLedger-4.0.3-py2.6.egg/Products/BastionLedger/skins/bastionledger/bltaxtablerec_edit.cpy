## Controller Python Script "blassetregister_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective, rate, code='', kw={}, id=''
##title=edit tax record properties
##
REQUEST=context.REQUEST

# if there is no id specified, keep the current one
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)
 
from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Tax Record %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

new_context.manage_edit(effective, rate, code, kw)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

