## Controlled Python Script "validate_timeperiods"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ratio='',min_hrs='',max_hrs='',defaults=[]
##title=Validates properties of a timesheet period
##
if not ratio:
    state.setError('ratio', 'Ratio required', 'ratio_required')
    try:
        ratio = float(ratio)
    except:
        state.setError('ratio', 'Invalid field', 'invalid field')

if not min_hrs:
    state.setError('min_hrs', 'Min Hours required', 'min_hrs_required')
    try:
        min_hrs = float(min_hrs)
    except:
        state.setError('min_hrs', 'Invalid field', 'invalid field')

if not max_hrs:
    state.setError('max_hrs', 'Max Hours required', 'max_hrs_required')
    try:
        max_hrs = float(max_hrs)
    except:
        state.setError('max_hrs', 'Invalid field', 'invalid field')


if not defaults:
    state.setError('defaults', 'defaults required', 'defaults_required')
elif not len(defaults) == 7:
    state.setError('defaults', 'Invalid field', 'invalid field')
else:
    ndx = 0
    for dow in context.select_day_of_week():
        day = defaults[ndx]
        try:
            day = float(day)
        except:
            state.setError(dow, 'Invalid field', 'invalid_field')
        ndx += 1

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

