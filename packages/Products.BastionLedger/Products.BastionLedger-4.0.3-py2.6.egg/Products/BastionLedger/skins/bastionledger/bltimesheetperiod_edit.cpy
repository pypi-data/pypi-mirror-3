## Controller Python Script "bltimesheetperiod_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ratio,min_hrs,max_hrs,defaults,id='',title='',
##title=edit timesheet periods
##
REQUEST=context.REQUEST

# if there is no id specified, keep the current one
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)
 
from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Asset Register %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

new_context.manage_edit(title, ratio, max_hrs, min_hrs, defaults)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

