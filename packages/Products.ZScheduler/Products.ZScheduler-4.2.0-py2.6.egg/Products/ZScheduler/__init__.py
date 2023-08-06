#
#    Copyright (C) 2004-2012  Corporation of Balclutha. All rights Reserved.
#
#    For your open source solution, bureau service and consultancy requirements,
#    visit us at http://www.balclutha.org or http://www.last-bastion.net.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import atexit, logging, transaction
import ZScheduler, ZScheduleEvent, FSZScheduleEvent
from App.ImageFile import ImageFile
from AccessControl import ModuleSecurityInfo
from AccessControl.Permissions import view
from Permissions import add_scheduler_events
from Acquisition import aq_base

from config import *

# optional plone stuff
try:
    import tool
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore import utils
    from Products.CMFCore.permissions import AddPortalContent
    registerDirectory(SKINS_DIR, GLOBALS)
    DO_PLONE=1
except:
    DO_PLONE=0

LOG = logging.getLogger('ZScheduler')
 
                                                                                
def initialize(context):
    """
    hook into control panel
    """
    context.registerClass(ZScheduleEvent.ZScheduleEvent,
                          constructors = (ZScheduleEvent.manage_addZScheduleEventForm,
                                          ZScheduleEvent.manage_addZScheduleEvent),
                          icon='www/event.gif',
                          permission=add_scheduler_events
                          )
    context.registerHelp()

    if DO_PLONE:
        utils.registerIcon(FSZScheduleEvent.FSZScheduleEvent, 'www/fsevent.gif', GLOBALS)

        utils.ToolInit('ZScheduler Tool',
                       tools=(tool.SchedulerTool,),
                       icon='tool.gif').initialize(context)


    try:
        from Zope2 import bobo_application
    except ImportError:
        bobo_application = None
    if bobo_application is not None:
        app = bobo_application()
    else:
        app = context._ProductContext__app

    cp = app.Control_Panel
    global scheduler

    if getattr(aq_base(cp), 'ZScheduler', None):
        LOG.info('moving ZScheduler from Control Panel')
        app._setObject('ZSchedulerTool', aq_base(cp.ZScheduler))
	cp._delObject('ZScheduler')
	scheduler = app.ZSchedulerTool
	scheduler._setId('ZSchedulerTool')
        transaction.get().commit()
    elif not getattr(app, 'ZSchedulerTool', None):
        app._setObject('ZSchedulerTool', ZScheduler.ZScheduler())
        #transaction.get().savepoint(optimistic=True)
        transaction.get().commit()

    scheduler = app.ZSchedulerTool
    try:
        # don't want to hang the server if an exception is raised ...
        scheduler._start()
    except Exception, e:
        LOG.error('scheduler worker start failed', exc_info=True)
        
    # clean up stuff on exit ...
    atexit.register(scheduler._stop)

misc_ = {}
for icon in ('scheduler', 'logrec', 'logger', 'timer'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, GLOBALS)

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('ZScheduler')
ModuleSecurityInfo('Products.ZScheduler').declarePublic('ZScheduleEvent')
ModuleSecurityInfo('Products.ZScheduler.ZScheduleEvent').declarePublic('parse_spec')


