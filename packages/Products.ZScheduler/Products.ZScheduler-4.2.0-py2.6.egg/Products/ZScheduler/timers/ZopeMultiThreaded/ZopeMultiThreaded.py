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
from threading import Thread
import AccessControl, transaction
from Products.ZScheduler.timers.ZopeSingleThreaded.ZopeSingleThreaded import ZopeSingleThreaded

class ZopeMultiThreaded(ZopeSingleThreaded):
    """
    Timer thread kicks off job(s) in their own detached thread.

    This has the benefit of most accurately maintaining job start times
    as the timer is not delayed in the task of dispatch by performing
    potentially long-running schedule events.
    """
    meta_type = 'ZopeMultiThreaded'

    def _dispatch(self, event):
        worker = Thread(None, self._invokeFromPath, ['/'.join(event.getPhysicalPath())])
        worker.setName(event.getId())
        worker.setDaemon(1)                # detach thread ...
        worker.start()
        
    def _invokeFromPath(self, event_path):
        # Set up the "application" object that automagically opens connections

        # TODO - fix all this up!!!
        conn = Globals.DB.open()
        app = self._getContext(conn.root()['Application'])

        app.unrestrictedTraverse(event_path).manage_invokeEvent()

        transaction.get().commit()
        conn.close()

AccessControl.class_init.InitializeClass(ZopeMultiThreaded)
