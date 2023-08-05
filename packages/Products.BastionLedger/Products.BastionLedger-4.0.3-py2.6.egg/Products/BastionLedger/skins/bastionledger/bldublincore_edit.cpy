## Controller Python Script "bldublincore_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',title='',description=''
##title=edit Dublin Core properties
##
REQUEST=context.REQUEST

# if there is no id specified, keep the current one
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

type = new_context.getPortalTypeName()

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited %s %s at %s' % (type, new_context.title_or_id(), new_context.absolute_url()))

new_context.plone_utils.contentEdit( new_context
                                   , id=id
                                   , title=title
                                   , description=description )
context.plone_utils.addPortalMessage('%s changes saved.' % type)
return state.set(context=new_context)
 

