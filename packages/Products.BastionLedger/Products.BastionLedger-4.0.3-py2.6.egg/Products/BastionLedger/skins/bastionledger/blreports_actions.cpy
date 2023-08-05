## Controller Python Script "blreports_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email='',ids=[]
##title=manage reports folder content
##
from Products.CMFCore.utils import getToolByName

request = context.REQUEST
reports = context.Reports

if request.has_key('form.button.Delete') and ids:
     reports.manage_delObjects(ids)
elif request.has_key('form.button.Paste'):
     reports.manage_pasteObjects(REQUEST=request)
elif request.has_key('form.button.Copy') and ids:
     cp = reports.manage_copyObjects(ids)
     request.RESPONSE.setCookie('__cp', cp, path='%s' % request.get('BASEPATH1', '/'))
elif request.has_key('form.button.Email'):
     member = getToolByName(context, 'portal_membership').getAuthenticatedMember()
     if member.hasProperty('email'):
         mfrom = member.getProperty('email')
     else:
         mfrom = getToolByName(context, 'portal_url').getPortalObject().getProperty('email_from_address')
     reports.manage_sendmail(ids, mfrom, email)
     getToolByName(context, 'plone_utils').addPortalMessage('Emailed report(s)')

return state

