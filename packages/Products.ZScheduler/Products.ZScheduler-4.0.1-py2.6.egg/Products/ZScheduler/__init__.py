#    Copyright (C) 2004-2011  Corporation of Balclutha. All rights Reserved.
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
import atexit, logging
import ZScheduler, ZScheduleEvent, FSZScheduleEvent
from App.ImageFile import ImageFile
from AccessControl import ModuleSecurityInfo, allow_module
from AccessControl.Permissions import view
from Permissions import add_scheduler_events
from Acquisition import aq_base

from config import *
import ZScheduleEvent

# optional plone stuff
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore import utils
    from Products.CMFCore.permissions import AddPortalContent
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    registerDirectory(SKINS_DIR, GLOBALS)
    DO_PLONE=1
except:
    DO_PLONE=0

LOG = logging.getLogger('ZScheduler')

# module level scheduler
scheduler = None
 
_security = ModuleSecurityInfo('Products.ZScheduler')
allow_module('Products.ZScheduler')
                                      
_security.declareProtected(view, 'getScheduler')
def getScheduler():
    """ returns the scheduler instance """
    return scheduler
                                                                                

def initialize(context):
    """
    hook into control panel
    """
    global scheduler
    try:
        context.registerClass(ZScheduleEvent.ZScheduleEvent,
                              constructors = (ZScheduleEvent.manage_addZScheduleEventForm,
                                              ZScheduleEvent.manage_addZScheduleEvent),
                              icon='www/event.gif',
                              permission=add_scheduler_events
                              )
        context.registerHelp()
    except:
        raise

    if DO_PLONE:
        utils.registerIcon(FSZScheduleEvent.FSZScheduleEvent, 'www/fsevent.gif', globals())

        # Register the extension profile
        try:
            profile_registry.registerProfile('default',
                                             PROJECTNAME,
                                             'ZScheduler',
                                             'profiles/default',
                                             PROJECTNAME,
                                             EXTENSION,
                                             IPloneSiteRoot)
        except KeyError:
            # duplicate entry ...
            pass

    # Add ZSchedule to Control Panel
    cp = getattr(context._ProductContext__app, 'Control_Panel', None)

    if cp:
        if not getattr(aq_base(cp), 'ZScheduler', None):
            LOG.info('Adding ZScheduler to Control Panel')
            cp._setObject('ZScheduler', ZScheduler.ZScheduler())
            scheduler = cp.ZScheduler
        else:
            scheduler = cp.ZScheduler
            try:
                # don't want to hang the server if an exception is raised ...
                scheduler._start()
            except Exception, e:
                LOG.error('scheduler worker start failed', exc_info=True)
            
        # clean up stuff on exit ...
        atexit.register(scheduler._stop)

misc_ = {}
for icon in ('scheduler', 'logrec', 'logger', 'timer'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, globals())

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('ZScheduler')
ModuleSecurityInfo('Products.ZScheduler').declarePublic('ZScheduleEvent')
ModuleSecurityInfo('Products.ZScheduler.ZScheduleEvent').declarePublic('parse_spec')


