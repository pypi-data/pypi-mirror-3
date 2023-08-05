## Controller Python Script "blshare_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,description,face,allocated,issue_date,voting_class,id=''
##title=edit share definition properties
##
REQUEST=context.REQUEST
 
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.editProperties(title, description, face, allocated, issue_date, voting_class)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited share definition %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

