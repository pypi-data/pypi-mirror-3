#    Copyright (C) 2005-2008  Corporation of Balclutha. All rights Reserved.
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
from ZScheduleEvent import ZScheduleEvent
from Products.CMFCore.FSObject import FSObject
from Products.CMFCore.utils import expandpath
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class FSZScheduleEvent(FSObject, ZScheduleEvent ):
    """
    A File system ZScheduleEvent
    """
    meta_type = 'FSZScheduleEvent'

    manage_options =  (
        {'label':'Customize', 'action':'manage_main'},
    ) + ZScheduleEvent.manage_options[1:-2]

    __ac_permissions__ = ZScheduleEvent.__ac_permissions__ + FSObject.__ac_permissions__
    manage_main = PageTemplateFile('zpt/fsevent', globals())

    def _createZODBClone(self):
        obj = ZScheduleEvent(self.getId(), self.title, self.callable, self.minute, 
                             self.hour, self.month, self.day_of_month, self.day_of_week, 
                             self.tz)
        return obj

    def __call__(self, *args, **kw):
        '''Calls the script.'''
        self._updateFromFS()
        return ZScheduleEvent.__call__(self, *args, **kw)

    def _readFile(self, reparse):

        """Read the data from the filesystem.

        Read the file (indicated by exandpath(self._filepath), and parse the
        data if necessary.
        """

        fp = expandpath(self._filepath)

        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try:
            lines = file.readlines()
        finally:
            file.close()

	tz = 'UTC'
        lino=0
        for line in lines:

            lino = lino + 1
            line = line.strip()

            if not line or line[0] == '#':
                continue

            try:
		if line.startswith('title='):
		    self.title = line[6:]
		elif line.startswith('tz='):
		    tz = line[3:]
		else:
		    # we don't want to schedule this yet ...
		    self.status = 0
		    minute,hour,month,day_of_month,day_of_week,callable_id = line.split(' ')
		    self.manage_editSchedule(tz, minute,hour,month,day_of_month,day_of_week, 0) 
		    self.callable_id = callable_id
	    except:
                raise ValueError, ( 'Error processing line %s of %s:\n%s' % (lino,fp,line) )

AccessControl.class_init.InitializeClass(FSZScheduleEvent)


registerFileExtension('sched', FSZScheduleEvent)
registerMetaType('ZScheduleEvent Object', FSZScheduleEvent)
