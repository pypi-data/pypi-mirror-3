## Controller Python Script "blemployee_add_timesheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=date,entries
##title=add a timesheet
##
REQUEST=context.REQUEST
from DateTime import DateTime
from Products.BastionLedger.BLPayroll import manage_addBLTimesheet

id = date.strftime('timesheet-%Y-%m-%d')
slots = map(lambda x: x.getId(), context.getTimesheetSlots())

for entry in entries:
    hours = 0.0
    if not entry.has_key('day') or not isinstance(entry['day'], DateTime):
        context.plone_utils.addPortalMessage('bad date(s)', 'error')
        return state.set(status='failure')
    for slot in slots:
        if not entry.has_key(slot) or not isinstance(entry[slot], float):

            context.plone_utils.addPortalMessage('non-numeric hour(s) %s' % entry.get(slot, slot), 'error')
            return state.set(status='failure')
        hours += entry[slot]
    if hours < 0.0 or hours > 24.0:
        context.plone_utils.addPortalMessage('invalid number of hours', 'error')
        return state.set(status='failure')


try:
    manage_addBLTimesheet(context, date, entries, id)
    context.plone_utils.addPortalMessage('Timesheet Added')
except KeyError, e:
    getattr(context, id).manage_edit(entries)
    context.plone_utils.addPortalMessage('Updated Timesheet')

return state

