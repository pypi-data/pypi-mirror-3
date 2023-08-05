## Controller Python Script "blattachments_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[],email='',files=[]
##title=add/delete attachments
##
REQUEST=context.REQUEST

if ids:
    if email:
        context.manage_emailAttachments(ids, email)
        context.plone_utils.addPortalMessage('Emailed to %s' % email)
    else:
        context.manage_delAttachments(ids)
        context.plone_utils.addPortalMessage('Deleted')
    return state

if files:
    for file in files:
        context.manage_addAttachment(file)
        context.plone_utils.addPortalMessage('Uploaded %i file(s)' % len(files))
    return state

context.plone_utils.addPortalMessage('Nothing to do')
return state
