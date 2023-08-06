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

import AccessControl
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog

from interfaces.IQueue import IQueue
from threading import Lock

from Acquisition import aq_base
from ZScheduleEvent import ZScheduleEvent
from Exceptions import ZSchedulingException

from zope.interface import implements

class ZQueue(ZCatalog):
    """
    This is a thread-safe queue of scheduled events and we're getting loads for free as
    we've set up a Date index on it's key ...
    """
    implements(IQueue)

    meta_type = 'ZQueue'
    title = 'ZQueue'
    _lock = Lock()
    manage_options = ZCatalog.manage_options[1:]
    manage_main = ZCatalog.manage_catalogView
    _security = ClassSecurityInfo()
    
    def all_meta_types(self):
        """ contain nothing """
        return []
    
    def __init__(self, id):
        ZCatalog.__init__(self, id)
        # TODO - implement status
        self.addIndex('time', 'DateIndex')
        self.addIndex('getPhysicalPath', 'PathIndex')
        self.addIndex('active', 'BooleanIndex')
        for name in ('time', 'meta_type',):
            self.addColumn(name)

    def pop(self, obj):
        """
        remove obj from catalog (actually just recatalog to force status change)
        """
        url = '/'.join(obj.getPhysicalPath())
        try:
            self._lock.acquire()
            ZCatalog.uncatalog_object(self, url)
            ZCatalog.catalog_object(self, obj, url)
        finally:
            self._lock.release()
            
    push = pop

    def get(self, url):
        try:
            self._lock.acquire()
            return self.getobject( self.getrid(url) )
        finally:
            self._lock.release()
            
    def delete(self, url):
	try:
            self._lock.acquire()
            self.uncatalog_object(url)
        finally:
            self._lock.release()
	
    def reload(self, REQUEST=None):
        """
        search ZODB for all ZScheduleEvents and place them in the queue
        """
        root = self.getPhysicalRoot()
        try:
            self._lock.acquire()
            #
            # hmmm - we'd really like to do this but this doesn't work
            # for (i) subclassed ZScheduleEvent's; or (ii) stuff not in
            # ObjectManager containment relationships :(
            #
            #    self.ZopeFindAndApply(root,
            #                          obj_metatypes=['ZScheduleEvent'],
            #                          search_sub=1,
            #                          apply_func=self.catalog_object,
            #                          apply_path='/'.join(root.getPhysicalPath()))
            self._reschedule(root)
        finally:
            self._lock.release()

        if REQUEST:
	    return self.manage_main(self, REQUEST)

    def getNext(self):
        try:
            self._lock.acquire()
            try:
                return self()[0].getObject()
            except:
                return None
        finally:
            self._lock.release()

    def _reschedule(self, folder):
        """
        tail-recursive ZODB rescheduler

        this function is designed to work with (i) subclasses of ZScheduleEvent;
        (ii) folder-like object attributes that aren't necessarily included in
        the _objects member ;)
        """
	try:
            objs = folder.objectValues()
	except Exception, e:
	    raise ZSchedulingException, '%s\n%s' % (folder.absolute_url(), str(e))

        # we are calling the ZCatalog stuff directly to avoid deadlock
        for e in filter( lambda x: isinstance(x, ZScheduleEvent), objs):
	    try:
                e.time = e.nextEventTime()
	    except:
		raise ZSchedulingException, e
            self.uncatalog_object('/'.join(e.getPhysicalPath()))
            self.catalog_object(e, '/'.join(e.getPhysicalPath()))

        # recurse through all sub-folders ...
        for sf in filter(lambda x: getattr(aq_base(x), 'objectValues', None), objs):
            try:
                self._reschedule(sf)
            except:
                # hmmm - non-iterable objects etc ...
                continue

    def _repair(self):
        try:
            self.addIndex('getPhysicalPath', 'PathIndex')
        except:
            pass
        try:
            self.addIndex('active', 'BooleanIndex')
        except:
            pass
        try:
            self.addColumn('meta_type')
        except:
            pass
        self.manage_reindexIndex(['time', 'getPhysicalPath', 'active'])

AccessControl.class_init.InitializeClass( ZQueue )
