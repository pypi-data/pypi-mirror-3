## Controller Python Script "blorder_email_invoice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email,message='',ids=[]
##title=email an invoice (or invoices), supports multiple email addresses
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

if not ids:
    if context.meta_type.find('Order') == -1:
        context.plone_utils.addPortalMessage('Please select some order(s)')
        return state.set(status='failure')
    orders = [ context ]
else:
    orders = filter(lambda x: x,
                    map(lambda x: getattr(context, x, None), ids))
for order in orders:
    for recipient in recipients:
        order.manage_emailInvoice(formataddr(recipient), message)

context.plone_utils.addPortalMessage('%i Order(s) emailed to %s' % (len(orders), ', '.join(map(lambda x: x[1], recipients))))
return state.set(status='success')
