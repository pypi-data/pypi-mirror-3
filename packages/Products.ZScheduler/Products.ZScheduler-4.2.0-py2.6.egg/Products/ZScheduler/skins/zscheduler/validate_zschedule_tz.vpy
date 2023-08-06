## Controlled Python Script "validate_zschedule_tz"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_tz=''
##title=Validates timezone
##
if not zse_tz:
    state.setError('zse_tz', 'Field Required', 'field_required')
elif not zse_tz in context.timezones():
    state.setError('zse_tz', 'Invalid Timezone', 'invalid_timezone')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state

