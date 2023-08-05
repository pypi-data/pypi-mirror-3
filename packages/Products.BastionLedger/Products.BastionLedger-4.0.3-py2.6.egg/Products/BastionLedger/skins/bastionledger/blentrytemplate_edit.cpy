## Controller Python Script "blentrytemplate_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=body,id='',title='',description=''
##title=edit asset register properties
##
REQUEST=context.REQUEST

# if there is no id specified, keep the current one
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)
 
from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Entry Templage %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

new_context.plone_utils.contentEdit( new_context
                                   , id=id
                                   , title=title
                                   , description=description )

new_context.ZPythonScript_edit('', body)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

