## Controlled Python Script "validate_attachments_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=files=[]
##title=Validates attachment files
##
from Products.CMFPlone import PloneMessageFactory as _

for file in files:

    if file is None:
        filename=None
    else:
        filename=getattr(file, 'filename', None)

    if not filename:
        state.setError('files', _(u'You must upload a file'))
        break

    alternative_id = filename[max( string.rfind(filename, '/')
                                  , string.rfind(filename, '\\')
                                  , string.rfind(filename, ':') )+1:].strip()

    #
    # attachments infrastructure is optional ...
    #
    attachments = getattr(context,'attachments', None)
    if attachments:
        id_err = context.attachments.check_id(alternative_id)
        if id_err:
            state.setError('files', id_err)
            break
        
    #if alternative_id in context.attachments.objectIds():
    #    state.setError('files', 'Filename already attached', 'id_error')
    #    break

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

