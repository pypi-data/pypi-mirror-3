## Controller Python Script "blledger_change_control_recalculate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=recalculate the amount in the GL for this journal
##

context.manage_recalculateControl()

context.plone_utils.addPortalMessage('Control Account Recalculated')
return state

