## Controller Python Script "blpayroll_run"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=date,ids=[]
##title=run payroll for specified date
##
context.manage_payEmployees(ids,date)

context.plone_utils.addPortalMessage('Payroll completed')
return state

