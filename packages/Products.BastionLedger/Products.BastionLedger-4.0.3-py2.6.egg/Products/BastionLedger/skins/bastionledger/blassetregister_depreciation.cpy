## Controller Python Script "blassetregister_depreciation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=date_start, date_end
##title=process asset register depreciation
##
REQUEST=context.REQUEST

date_range = (date_start, date_end)

if REQUEST.has_key('form.button.Post'):
    context.manage_applyDepreciation(date_range)
    context.plone_utils.addPortalMessage('Posted Depreciation')
elif REQUEST.has_key('form.button.Apply'):
    for asset in context.objectValues('BLAsset'):
        asset.manage_changeProperties(depreciation_to_date=asset.depreciation(date_range),
                                      last_depreciation_run=date_end)
    context.plone_utils.addPortalMessage('Applied depeciations')

return state

