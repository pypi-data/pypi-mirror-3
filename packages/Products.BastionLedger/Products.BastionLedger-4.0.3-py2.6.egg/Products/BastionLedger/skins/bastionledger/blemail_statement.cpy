## Controller Python Script "blemail_statement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email,sender='',effective=None
##title=email financial statement
##

REQUEST = context.REQUEST

if REQUEST.has_key('form.button.BalanceSheet'):
    template='blbalancesheet_template'
elif REQUEST.has_key('form.button.RevenueStatement'):
    template='blbalancesheet_template'
elif REQUEST.has_key('form.button.Cashflow'):
    template='blcashflow_template'
else:
    raise AssertionError, 'unknown action'

context.manage_emailStatement(email, sender, template, effective or DateTime())

context.plone_utils.addPortalMessage('Emailed report to %s' % email)

return state

