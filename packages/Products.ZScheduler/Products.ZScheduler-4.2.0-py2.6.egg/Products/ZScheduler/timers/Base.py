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
import Globals, zLOG
from AccessControl.Permissions import change_configuration
from AccessControl import SecurityManagement, User
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.ZScheduler.interfaces.ITimer import ITimer

from threading import Thread, Event

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

# need a handle to the thread ...
worker = None


class BaseTimer(PropertyManager, SimpleItem):
    """
    Basic timer implementation (ZMI + start/stop)
    """
    __implements__ = (ITimer,)

    id = 'timer'

    _stop_event = Event()

    icon = 'misc_/ZScheduler/timer'

    _properties = (
          {'id':'is_active', 'mode':'w', 'type':'boolean'},
        )

    manage_options = PropertyManager.manage_options + (
        {'label':'Restart', 'action':'manage_restart' },
        ) + SimpleItem.manage_options
    manage_main = PropertyManager.manage_propertiesForm
    property_extensible_schema__ = 0

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (change_configuration, ('manage_restart',)),
       ) + SimpleItem.__ac_permissions__

    def __init__(self):
        self.is_active = False

    def title(self):
        return self.meta_type

    def _start(self, scheduler=None):
        """
        start timer

        essentially just clears the stop semaphore causing the main loop to run
        """
        self._stop_event.clear()

    def _stop(self, scheduler=None):
        """
        stop timer

        essentially just flags the stop semaphore and the main loop should drop out
        """
	self._stop_event.set()
        scheduler = scheduler or self.aq_parent
        scheduler.semaphore.set()

    def isActive(self):
        """
        hard-core function testing underlying timer mechanism's status
        """
        return False

    def _load(self):
        """
        load underlying timer
        """
        pass

    def _unload(self):
        """
        unload underlying timer
        """
        pass


    def manage_restart(self, scheduler=None, REQUEST=None):
        """
        stop/start the timer
        """
        self._stop(scheduler or self.aq_parent)
        self._start(scheduler or self.aq_parent)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Restarted')
            return self.manage_main(self, REQUEST)

Globals.InitializeClass(BaseTimer)


class ThreadedTimer(BaseTimer):
    """
    A timer that manages load/reload in a separate thread

    Note that Zope connections do not play well with threads - the connection
    is in another thread.  However, since we're not doing any writes/commits
    in our worker thread, this doesn't affect us.

    Refer to http://www.zopelabs.com/cookbook/1058719806 for a discussion
    about Zope Threads.
    """
    def _start(self, scheduler=None):
	"""
	kick off a listener to refresh crontab's as event's change or are added
	and removed
	"""
        zLOG.LOG('ZScheduler.timer.%s' % self.meta_type, zLOG.INFO, 'starting...')
        if not self.is_active:
            return

        # at app server startup, we don't have a REQUEST - needed to render ZPT
        if not getattr(self, 'REQUEST', None):
            self = self._getContext(self)

        scheduler = scheduler or self.aq_parent

        BaseTimer._start(self, scheduler)

        worker = Thread(None, self._run)
        worker.setName('ZScheduler')
        worker.setDaemon(1)          # detach thread ...
        worker.start()

        # force the run() function to invoke - ie load ... 
        # this is is essentially non-blocking
        scheduler.semaphore.set()

    def _run(self):
        """
        this is our reload procedure
        """
        zLOG.LOG('ZScheduler.timer.%s' % self.meta_type, zLOG.INFO, 'starting listener')
        # ensure system user priviledges
        SecurityManagement.newSecurityManager(None, User.system)

        while 1:
            if self._stop_event.isSet(): 
                zLOG.LOG('ZScheduler.timer.%s' % self.meta_type, zLOG.INFO, 'stopping listener')
                return

            # we need to reopen the connection each time to access the committed changes ...

            # Set up the "application" object that automagically opens connections
            conn = Globals.DB.open()
            app = self._getContext(conn.root()['Application'])
            scheduler = app.ZSchedulerTool

            scheduler.timer._unload()
            scheduler.timer._load()

            scheduler.semaphore.wait()
            # we were interrupted ...
            if scheduler.semaphore.isSet():
                scheduler.semaphore.clear()

            conn.close()
            
    def _stop(self, scheduler):
	"""
	remove crontab
	"""
        zLOG.LOG('ZScheduler.timer.%s' % self.meta_type, zLOG.INFO, 'stopping...')
        BaseTimer._stop(self, scheduler)

        if not self.is_active:
            return
        
        self._unload()

    def _getContext(self, app):
        """
        set up a Zope context
        """
        resp = HTTPResponse(stdout=None)

        from asyncore import socket_map
        http = filter(lambda x:x.__class__.__name__ == 'zhttp_server', socket_map.values())[0]

        env = {
            'SERVER_NAME': http.server_name,
            'SERVER_PORT': str(http.server_port),
            'REQUEST_METHOD':'GET'
            }
        req = HTTPRequest(None, env, resp)
        return app.__of__(RequestContainer(REQUEST = req))

Globals.InitializeClass(ThreadedTimer)
