#    Copyright (C) 2004-2009  Corporation of Balclutha. All rights Reserved.
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

import AccessControl, Products, DateTime, threading, os, transaction, urlparse
from AccessControl.Permissions import view_management_screens, change_configuration, access_contents_information
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZQueue import ZQueue
from Log import Logger, LogSupport
from timers import timers

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

devnull = open('/dev/null', 'r+')

class ZScheduler ( PropertyManager, LogSupport ) :
    """
    An event scheduler

    This class provides the ZMI wrapper which delegates to it's two
    internal structures, a queue containing the events, and a timer
    which dispatches them.
    """
    meta_type = 'ZScheduler'
    icon='misc_/ZScheduler/scheduler'
    id = 'ZScheduler'
    title = 'Event Scheduler'

    # this guys lives in memory not ZODB ...
    semaphore = threading.Event()
    
    property_extensible_schema__ = 0
    _properties = (
        {'id':'timezone',  'type':'selection',          'mode':'w',
         'select_variable': 'timezones' },
        {'id':'callables', 'type':'multiple selection', 'mode':'w',
         'select_variable': 'products'},
        {'id':'timer_type','type':'selection',          'mode':'w',
         'select_variable': 'timers'},
        {'id':'queue_batch_size', 'type':'int', 'mode':'w'},
        ) + LogSupport._properties

    __ac_permissions__ = (
        (access_contents_information, ('isActive', 'isScheduled', 'nextEvent')),
        (view_management_screens, ('manage_timer', 'manage_log',
                                   'timezones', 'products', 'timers', 'queue', 'logger')),
        (change_configuration, ('manage_delete', 'manage_unschedule', 'manage_reload', 'schedule', 'unschedule')),
        ) + PropertyManager.__ac_permissions__ + LogSupport.__ac_permissions__
    
    manage_options = (
        {'label':'Queue',      'action':'manage_main',
         'help':('ZScheduler', 'queue.stx')},
        {'label':'Timer',      'action':'manage_timer',
         'help':('ZScheduler', 'timer.stx')},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('ZScheduler', 'props.stx')}, ) + LogSupport.manage_options

    manage_main  = PageTemplateFile('zpt/queue', globals())

    def manage_timer(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('timer/manage_main')

    def __init__(self):
        LogSupport.__init__(self)
        self.callables = ['Script (Python)', 'DTML Method']
        self.timezone = 'UTC'
        self.timer_type = ''
        self.timer = None
        self.queue_batch_size = 15
        self.log_batch_size = 15
        self._queue = ZQueue('queue')

    def manage_afterAdd(self, item, container):
        self._queue.manage_afterAdd(self._queue, self)
        # create our timer
        self._updateProperty('timer_type', 'Dummy')
        # and load it ...
        self.semaphore.set()

    def timezones(self):
        """ available timezones """
        return DateTime.Timezones()

    def products(self):
        """ available callable products """
        results = filter( lambda x: x not in ['ZScheduleEvent'],
                          map( lambda x: x['name'], Products.meta_types ) )
        results.sort()
        return results

    def timers(self):
        return timers()

    def schedule(self, event):
        """
        add/reschedule this event
        """
        try:
            self._queue.pop(event)
        except:
            pass
        self._queue.push(event)
        event.time = event.nextEventTime()
        transaction.get().commit()
        self.semaphore.set()

    def unschedule(self, event):
        """
        remove event from schedule
        """
        try:
            self._queue.pop(event)
            transaction.get().commit()
            self.semaphore.set()
        except Exception, e:
            pass
        
    def isScheduled(self, event):
        """
        returns whether or not the event is in our queue
        """
        try:
            ob = self._queue.get('/'.join(event.getPhysicalPath()))
            return True
        except:
            return False

    def manage_delete(self, urls, REQUEST=None):
        """
        Remove item(s) from ZODB - well just the catalog actually, as
        we keep on zapping ourselves with this!
        """
        for url in urls:
	    try:
                event = self._queue.get(url)
                event.aq_parent._delObject(event.getId())
	    except:
		self._queue.delete(url)

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_unschedule(self, urls, REQUEST=None):
        """
        Remove item(s) from queue
        """
	root = self._queue.getPhysicalRoot()
	for url in urls:
	    try:
		event = root.unrestrictedTraverse(url)
	    except:
		self._queue.delete(url)
		continue
	    self._queue.pop(event)
		
        transaction.get().commit()
        # tell timer to reset
        self.semaphore.set()
        if REQUEST:
            return self.manage_main(self, REQUEST)
            
    def manage_reload(self, REQUEST=None):
        """
        Reload queue by recreating it from a ZScheduleEvents in the ZODB
        """
        # find events
        self._queue.reload()
        transaction.get().commit()
        # tell timer to reset
        self.semaphore.set()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_refresh(self, REQUEST={}):
        """
        Refresh queue by removing anything that no longer exists
        """
	root = self._queue.getPhysicalRoot()
	for url in map(lambda x: x.getPath(), self.queue(REQUEST)):
	    try:
		root.unrestrictedTraverse(url).manage_schedule()
	    except:
		self._queue.delete(url)
        if REQUEST:
	    return self.manage_main(self, REQUEST)

    def manage_schedule(self, urls, REQUEST=None):
        """
        Reschedule selected items
        """
	root = self._queue.getPhysicalRoot()
	for url in urls:
	    try:
		event = root.unrestrictedTraverse(url)
	    except:
		self._queue.delete(url)
		continue
	    self.schedule(event)
		
        transaction.get().commit()
        # tell timer to reset
        self.semaphore.set()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _updateProperty(self, id, value):
        """
        can't be arsed painting a custom properties page, but we need
        to dynamically change our timer implementation ...
        """
        if id == 'timer_type':
            if self.timer_type != value:
                self.timer and self.timer._stop(self)
                exec """
from timers.%s.%s import %s
self.timer = %s()
""" % (value, value, value, value)
                self.timer._start(self)
        PropertyManager._updateProperty(self, id, value)

    def queue(self, REQUEST={}):
        """ query the queue """
        query = dict(REQUEST)

        if not query.has_key('sort_on'):
            query['sort_on'] = 'time'
        if not query.has_key('sort_order'):
            query['sort_order'] = 'ascending'

        return self._queue(REQUEST=query)

    def events(self, REQUEST={}):
        """
        return the events in the queue

        We include request objects with these also so they work
        properly in *normal* Zope contexts as per our thread invokations

        You can pass 'time' queries if you wish ...
        """
        events = []

        proto, domain, directory, parameters, query, fragment = urlparse.urlparse(self.absolute_url())
        if domain.find(':') != -1:
            server_name, server_port = domain.split(':')
        elif proto == 'http':
            server_name, server_port = domain, '80'
        elif proto == 'https':
            server_name, server_port = domain, '443'
        else:
            # hmmm - should we worry about ftp ...
            raise ValueError, proto

        resp = HTTPResponse(stdout=devnull)
        os.environ['SERVER_NAME']    = server_name
        os.environ['SERVER_PORT']    = server_port
        os.environ['SERVER_URL']     = 'http://%s:%s' % (server_name, server_port)
        os.environ['REQUEST_METHOD'] = 'GET'
        request = HTTPRequest(devnull, os.environ, resp)

        for event in self.queue(REQUEST):
            try:
                events.append(event.getObject())
            except:
                continue

        return map(lambda x,y=request: x.__of__(RequestContainer(REQUEST=y)), events)

    def nextEvent(self):
        return self._queue.getNext()

    def _start(self):
        """ kick off the timer """
        self.timer._start(self)

    def _stop(self):
        """ clean up on exit """
        self.timer._stop(self)

    def isActive(self):
        """ determine if timer is actually running """
        return self.timer.isActive()

    def manage_restartTimer(self, REQUEST=None):
        """
        kick the timer in the guts
        """
        self.timer.manage_restart(self)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Restarted timer')
            return self.manage_main(self, REQUEST)

    def manage_repair(self, REQUEST=None):
	"""
	fix catalog(s)
	"""
        for brain in self.queue():
            try:
                ob = brain.getObject()
            except:
                self._queue.uncatalog_object(brain.getPath())

        LogSupport.manage_repair(self)

        # tell timer to reset
        self.semaphore.set()

	if REQUEST:
	    REQUEST.set('manage_tabs_message', 'Repaired')
	    return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(ZScheduler)
