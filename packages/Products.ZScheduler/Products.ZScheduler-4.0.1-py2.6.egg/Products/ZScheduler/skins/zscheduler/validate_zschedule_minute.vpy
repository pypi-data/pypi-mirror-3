## Controlled Python Script "validate_zschedule_minute"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_minute
##title=Validates minute range
##
from Products.ZScheduler.ZScheduleEvent import parse_spec

if not zse_minute:
    state.setError('zse_minute', 'Minute Required', 'minute_required')
elif not parse_spec(zse_minute, 0, 59):
    state.setError('zse_minute', 'Invalid format', 'invalid_format')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

