## Controller Python Script "blquotemgr_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderbooks=[], expiry_days=0, disclaimer='', base_currency='USD', email='', id='', title='', description=''
##title=edit quote manager properties
##
REQUEST=context.REQUEST

# if there is no id specified, keep the current one
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)
 
from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Quote Manager %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

new_context.plone_utils.contentEdit( new_context
                                   , id=id
                                   , title=title
                                   , description=description )

new_context.edit(orderbooks, disclaimer, expiry_days, base_currency, email)
context.plone_utils.addPortalMessage('Properties Updated')

return state.set(context=new_context)

