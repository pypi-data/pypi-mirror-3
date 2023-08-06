## Controller Python Script "zschedule_event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=zse_minute, zse_hour, zse_day_of_month, zse_day_of_week, zse_month, zse_tz
##title=edit schedule event properties
##
REQUEST=context.REQUEST
 
context.manage_editSchedule(zse_tz, zse_minute, zse_hour, zse_month, zse_day_of_month, zse_day_of_week)
context.plone_utils.addPortalMessage('Scheduling properties updated')
return state

