## Controlled Python Script "validate_zschedule_hour"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_hour
##title=Validates hour range
##
from Products.ZScheduler.ZScheduleEvent import parse_spec

if not zse_hour:
    state.setError('zse_hour', 'Hour Required', 'hour_required')
elif not parse_spec(zse_hour, 0, 23):
    state.setError('zse_hour', 'Invalid format', 'invalid_format')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

