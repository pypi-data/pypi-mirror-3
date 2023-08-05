## Controlled Python Script "validate_zschedule_month"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_month
##title=Validates month range
##
from Products.ZScheduler.ZScheduleEvent import parse_spec

if not zse_month:
    state.setError('zse_month', 'Month Required', 'month_required')
elif not parse_spec(zse_month, 1, 12):
    state.setError('zse_month', 'Invalid format', 'invalid_format')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

