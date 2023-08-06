## Controller Python Script "prefs_zscheduler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=urls=[]
##title=schedule/unschedule events
##
if context.REQUEST.has_key('form.button.Unschedule') and urls:
    context.portal_crontab.unschedule(urls)
    context.plone_utils.addPortalMessage('Unscheduled events')
elif context.REQUEST.has_key('form.button.Schedule') and urls:
    context.portal_crontab.schedule(urls)
    context.plone_utils.addPortalMessage('Scheduled events')
elif not urls:
    context.plone_utils.addPortalMessage('Please select some event(s)')
    state.set(status='failure')

else:
    context.plone_utils.addPortalMessage('Eek - no action specified')
    state.set(status='failure')

return state
