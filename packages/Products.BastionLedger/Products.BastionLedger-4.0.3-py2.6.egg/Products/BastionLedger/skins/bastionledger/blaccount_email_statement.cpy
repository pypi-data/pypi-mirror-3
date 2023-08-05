## Controller Python Script "blaccount_email_statement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email,message='',effective=None
##title=email a statement
##
from Products.CMFCore.utils import getToolByName
from email.Utils import getaddresses, formataddr

rt = getToolByName(context, 'portal_registration')

try:
    recipients = getaddresses(email.split(','))
except Exception, e:
    state.setError(field, _(u'You entered an invalid email address.'), 'invalid_email')
    return state.set(status='failure')

for realname, emailaddr in recipients:    
    if not rt.isValidEmail(emailaddr):
        state.setError(field, _(u'You entered an invalid email address.'), 'invalid_email')
        return state.set(status='failure')

for recipient in recipients:
    context.manage_emailStatement(formataddr(recipient), message, effective or DateTime())

context.plone_utils.addPortalMessage("Statement emailed to %s" % ', '.join(map(lambda x: x[1], recipients)))

return state.set(status='success')
