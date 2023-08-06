#
#    Copyright (C) 2011  Corporation of Balclutha. All rights Reserved.
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
import AccessControl
from AccessControl.Permissions import change_configuration
from Products.ZScheduler.config import TOOLNAME
from Products.ZScheduler.interfaces import ISchedulerTool
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import registerToolInterface, UniqueObject
from zope.interface import implements

class SchedulerTool(UniqueObject, ActionProviderBase, SimpleItem):
    """
    A tool to manage scheduled events in your portal
    """
    meta_type = portal_type = 'SchedulerTool'

    implements(ISchedulerTool)

    id = TOOLNAME
    title = 'Scheduled Events Tool'
    _actions = ()

    __ac_permissions__ = SimpleItem.__ac_permissions__ + (
        (change_configuration, ('eventValues', 'queueValues', 'timezone', 
                                'schedule', 'unschedule')),
        ) +  ActionProviderBase.__ac_permissions__

    manage_options = ActionProviderBase.manage_options + \
        SimpleItem.manage_options


    def __init__(self, id=TOOLNAME):
        pass

    def queueValues(self):
        """
        """
        tool = self.getPhysicalRoot().ZSchedulerTool
        query = {'getPhysicalPath': '/'.join(self.aq_parent.getPhysicalPath()) }
        return map(lambda x: x.getObject(), tool.searchResults(**query))

    def timezone(self):
        """
        """
        tool = self.getPhysicalRoot().ZSchedulerTool
        return tool.timezone

    def schedule(self, urls):
        """
        start scheduling the indicated urls
        """
        my_url = '/'.join(self.aq_parent.getPhysicalPath())
        tool = self.getPhysicalRoot().ZSchedulerTool
        tool.manage_schedule(filter(lambda x: x.startswith(my_url), urls))
        
    def unschedule(self, urls):
        """
        stop scheduling the indicated urls
        """
        my_url = '/'.join(self.aq_parent.getPhysicalPath())
        tool = self.getPhysicalRoot().ZSchedulerTool
        tool.manage_unschedule(filter(lambda x: x.startswith(my_url), urls))

AccessControl.class_init.InitializeClass(SchedulerTool)


registerToolInterface(TOOLNAME, ISchedulerTool)
