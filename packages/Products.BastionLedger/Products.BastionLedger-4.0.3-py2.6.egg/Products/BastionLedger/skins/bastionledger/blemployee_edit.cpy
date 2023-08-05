## Controller Python Script "blemployee_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,email,date_of_birth=DateTime(0), address='',phone='',tax_number='',bank_account='',super_number='',super_details='',description='',id=''
##title=edit part properties
##
REQUEST=context.REQUEST

if not id:
     id = context.getId()
new_context = context.portal_factory.doCreate(context, id)
 
new_context.manage_edit_public(title=title,
                               description=description,
                               email=email,
                               address=address,
                               phone=phone,
                               tax_number=tax_number,
                               bank_account=bank_account,
                               date_of_birth=date_of_birth,
                               super_number=super_number,
                               super_details=super_details)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited employee %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

