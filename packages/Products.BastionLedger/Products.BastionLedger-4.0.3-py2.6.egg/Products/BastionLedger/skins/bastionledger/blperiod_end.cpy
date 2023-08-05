## Controller Python Script "blperiod_end"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective,rerun=False
##title=perform period-end processing for ledger
##
request = context.REQUEST
from Products.BastionLedger.utils import floor_date
from Products.CMFPlone.utils import transaction_note

# place TZ in effective
effective = floor_date(DateTime('%s %s' % (effective, context.timezone)))

if request.has_key('form.button.Reports'):
    context.manage_periodEndReports(effective)
    context.plone_utils.addPortalMessage('Rerun reports')
if request.has_key('form.button.Run') or request.has_key('form.button.Rerun'):
    context.manage_periodEnd(effective, force=request.has_key('form.button.Rerun'))
    context.plone_utils.addPortalMessage('Ran period end for %s' % context.toLocalizedTime(effective))
elif request.has_key('form.button.Reset'):
    context.portal_bastionledger.periodend_tool.manage_reset(context)
    transaction_note('Reset period ends for %s at %s' % (context.title_or_id(), context.absolute_url()))
    context.plone_utils.addPortalMessage('Reinitialized all period end processing')
    
return state

