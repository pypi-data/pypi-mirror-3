## Controller Python Script "blforecaster_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=recs=[]
##title=update forecasts
##
REQUEST=context.REQUEST

context.manage_editForecasts(recs)

context.plone_utils.addPortalMessage('Forecasts Updated')
return state
