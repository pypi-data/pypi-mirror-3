#
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
import AccessControl, transaction
from Products.ZScheduler.interfaces.ITimer import ITimer
from threading import Thread
from DateTime import DateTime
from Acquisition import aq_base
from Products.ZScheduler.timers.Base import ThreadedTimer

# need a handle to the thread ...
worker = None

class ZopeSingleThreaded(ThreadedTimer):
    """
    A single-threaded timer which goes to sleep, waking to fire the next event in the queue
    """        
    meta_type = 'ZopeSingleThreaded'

    def _load(self):
        while 1:
            event = scheduler.nextEvent()
            while event:
                now = DateTime()
                e_time = event.time.timeTime()
                interval = e_time - now.timeTime()
            
                scheduler.semaphore.wait(interval)
                
                now = DateTime()
                if e_time - now.timeTime() <= 0:
                    self._dispatch(event)

    def _dispatch(self, event):
        """
        overrideable dispatching driver
        """
        event.manage_invokeEvent()
        transaction.get().commit()

AccessControl.class_init.InitializeClass(ZopeSingleThreaded)
