## Controller Python Script "blquote_email"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email='',message=''
##title=send job quotation
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
        context.plone_utils.addPortalMessage('Bad email address(s): %s' % str(e))
        return state.set(status='failure')


for recipient in recipients:
    context.manage_send(formataddr(recipient), message)

context.plone_utils.addPortalMessage('Emailed to %s' % ', '.join(map(lambda x: x[1], recipients)))
return state
