## Controller Python Script "blemployee_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=salary,hourly_rate,basis,start_day,tax_code='',accrued_leave=0.0,sick_days=0.0,department=''
##title=edit employee pay calculation info
##
REQUEST=context.REQUEST
 
context.manage_edit_private(start_day,department,salary,hourly_rate,basis,tax_code,accrued_leave,sick_days)

context.plone_utils.addPortalMessage('Properties Updated')
return state

