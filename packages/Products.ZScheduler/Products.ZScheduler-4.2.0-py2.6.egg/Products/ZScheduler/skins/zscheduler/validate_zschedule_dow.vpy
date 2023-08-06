## Controlled Python Script "validate_zschedule_dow"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_day_of_week
##title=Validates day of week range
##
from Products.ZScheduler.ZScheduleEvent import parse_spec

if not zse_day_of_week:
    state.setError('zse_day_of_week', 'Day of Week Required', 'dom_required')
elif not parse_spec(zse_day_of_week, 0, 7):
    state.setError('zse_day_of_week', 'Invalid format', 'invalid_format')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

