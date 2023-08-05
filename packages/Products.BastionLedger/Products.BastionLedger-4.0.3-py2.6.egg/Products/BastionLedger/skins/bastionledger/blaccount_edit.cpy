## Controller Python Script "blaccount_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,description,type,subtype,currency,accno,tags=[],email='',address=''
##title=edit part properties
##
REQUEST=context.REQUEST

id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

#
# do currency check
#
if currency != context.base_currency:
    if currency not in context.Currencies():
        state.setError('currency', 'Unsupported Currency', 'unsupported_currency')

    if state.getErrors():
        context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
        return state.set(status='failure')

new_context.manage_edit(title, description, type, subtype, accno, tags, currency)

# email is only present for subsidiary accounts ...
if context.hasProperty('email'):
    context.manage_changeProperties(email=email)
if context.hasProperty('address'):
    context.manage_changeProperties(address=address)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited account %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Account Properties Updated')

return state.set(context=new_context)

