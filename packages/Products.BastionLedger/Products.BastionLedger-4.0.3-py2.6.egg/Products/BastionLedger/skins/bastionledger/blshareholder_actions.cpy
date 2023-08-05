## Controller Python Script "blshareholder_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email,share,effective=None,message=''
##title=functions on shareholders
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


if context.REQUEST.has_key('form.button.EmailCert'):
    for recipient in recipients:
        context.manage_emailShareCertificate(formataddr(recipient), share, message, effective or DateTime())

    context.plone_utils.addPortalMessage("Share certificate emailed to %s" % ', '.join(map(lambda x: x[1], recipients)))

return state.set(status='success')
