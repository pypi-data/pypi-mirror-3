## Controller Python Script "blaccount_taxgroups_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',ids=[],tax_codes={}
##title=edit account tax groups
##
REQUEST=context.REQUEST
 
if REQUEST.has_key('form.button.Add'):
    context.manage_addTaxGroup(id)
elif REQUEST.has_key('form.button.Delete'):
    context.manage_delTaxGroups(ids)
elif REQUEST.has_key('form.button.Edit'):
    context.manage_editTaxCodes(tax_codes)

context.plone_utils.addPortalMessage('Tax groups Updated')

return state

