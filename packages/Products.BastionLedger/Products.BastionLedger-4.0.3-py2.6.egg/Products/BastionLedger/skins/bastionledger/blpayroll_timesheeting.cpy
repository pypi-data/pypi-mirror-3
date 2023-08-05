## Controller Python Script "blpayroll_timesheeting"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=edit timesheeting properties
##

REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note

if REQUEST.has_key('form.button.Settings'):
   context.manage_editTimesheetProps(REQUEST['timesheet_day'], 
                                     REQUEST.get('timesheets_required', False))


   transaction_note('Edited Payroll timesheeting %s at %s' % (context.title_or_id(), context.absolute_url()))
   context.plone_utils.addPortalMessage('Timesheeting Properties Updated')

elif REQUEST.has_key('form.button.Delete'):
   ids = REQUEST.get('ids',[])
   if ids:
       context.manage_delObjects(ids)

elif REQUEST.has_key('form.button.Change'):
   for period in REQUEST['period']:
      try:
          p = getattr(context, period['id'])
          p.manage_edit(period['title'],
                        float(period['ratio']),
			float(period['max_hrs']),
                        float(period['min_hrs']),
                        map(lambda x: float(x), period['defaults']))
      except:
          context.plone_utils.addPortalMessage('Bad/non-numeric period data')
          return state.set(status='failure')
   context.plone_utils.addPortalMessage('Changed properties')

elif REQUEST.has_key('form.button.Add'):
   try:
        id = REQUEST['title'].lower()
        factory = context.manage_addProduct['BastionLedger'].manage_addBLTimesheetSlot
        factory(id,
                title=REQUEST['title'],
                ratio=float(REQUEST['ratio']),
		max_hrs=float(REQUEST['max_hrs']),
                min_hrs=float(REQUEST['min_hrs']),
                defaults=map(lambda x: float(x), REQUEST['defaults']))
        context.plone_utils.addPortalMessage('Added period %s' % id)
   except:
        raise
        context.plone_utils.addPortalMessage('Failed adding period - make sure your fields are numeric and title not already added')
        return state.set(status='failure')

return state

