## Controller Python Script "ledger_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title,currency,timezone,description='',company_number='',incorporation_date=None,address='',directors=[],secretary='',tax_number='',industry_code='', id=''
##title=edit ledger properties
##
if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)

new_context.edit(title, description, company_number, incorporation_date,
                 address, directors, secretary, tax_number, industry_code,
                 currency,timezone)

new_context.plone_utils.addPortalMessage('Properties Updated')

return state.set(context=new_context)

