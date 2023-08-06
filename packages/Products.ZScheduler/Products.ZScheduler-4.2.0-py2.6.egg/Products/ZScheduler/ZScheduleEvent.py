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

import AccessControl, re, string
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import DateTime
from Acquisition import aq_base
from Log import Logger, LogSupport
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, change_configuration, view
from Permissions import execute_scheduler_events
from interfaces import IScheduleEvent
from zope.interface import implements

valid_char_number = re.compile(r'''^\d+$''')
valid_char_list = re.compile(r'''^\d+(-\d+)*(/\d+)*$''')
numbers = re.compile(r'''(\d+)''')

def parse_spec(specification, min, max):
    """
    crontab spec parser/validater
    """
    specification.replace(' ', '')
    if specification == '*': return 1
    for element in specification.split(','):
        if not valid_char_number.match(element):
            if not valid_char_list.match(element):
                return 0
            else:
                begin,end=element.split('-')
                if end.find('/') != -1:
                    end,increment=end.split('/')
                    if not valid_char_number.match(increment):
                        return 0
                if not valid_char_number.match(begin) and not valid_char_number.match(end):
                    return 0
        else:
            if int(element) < min or int(element) > max:
                return 0
    return 1

def expand_spec(specification):
    """
    take  a-b/c and produce a comma-separated list of expanded numbers
    this is a prereq for plone4cron
    """
    specification = specification.replace(' ', '')

    if specification.find(',') != -1:
        parts = specification.split(',')
        return ','.join(map(lambda x: expand_spec(x), parts))

    mod = 0

    if specification.find('/') != -1:
        specification, mod = specification.split('/')
        mod = int(mod)

    if specification.find('-') != -1:
        smin, smax = specification.split('-')
        smin = int(smin)
        smax = int(smax)
        values = range(smin, smax + 1)
    else:
        values = [specification]

    if mod:
        tmp = [smin]
        while smin < smax:
            smin += mod
            if smin <= smax:
                tmp.append(smin)
        values = tmp

    return ','.join(map(lambda x: str(x), values))
        

def get_first_time_for_spec(specification, min):
    """
    return the first valid number from the spec
    """
    if specification == '*':
        return min
    match = numbers.search(specification)
    return match.group(0)
    
def get_time_for_spec(specification, value, min, max):
    """
    specification is a crontab range, value is what you currently have, min
    and max are the boundaries to this time component

    returns a tuple of the next valid value and a flag indicating if
    it had to wrap to discover this - an indication to increment the next
    time component ;)
    """
    if specification == '*': 
        expansion = range(min, max + 1)
    else:
        expansion = []
        for element in specification.split(','):
            if valid_char_number.match(element):
                expansion.append(int(element))
            else:
                begin,end=element.split('-')
                begin = int(begin)
                if end.find('/') != -1:
                    end,increment=end.split('/')
                    end = int(end)
                    increment = int(increment)
                    index = begin
                    while index <= end:
                        expansion.append(index)
                        index += increment
                else:
                    end = int(end)
                    expansion.extend( range( begin, end + 1 ) )

    expansion.sort()

    for element in expansion:
        if element >= value:
            return (element, 0)
    return (expansion[0], 1)

def next_day(tm, tz):
    """
    returns the beginning of the next day, allowing for month/year rollover
    """
    m = tm.month()
    y = tm.year()
    month_len = tm._month_len[(y%4==0 and (y%100!=0 or y%400==0))][m]
    d = tm.day()
    if d < month_len:
        return DateTime.DateTime('%s/%s/%0.2i 00:00 %s' % (y, tm.mm(), d+1, tz))
    else:
        return next_month(tm, tz)

def next_month(tm, tz):
    """
    returns the beginning of the next month, allowing for year rollover
    """
    month = tm.month()
    if month == 12:
        return DateTime.DateTime('%i/01/01 00:00 %s' % (tm.year() + 1, tz))
    else:
        return DateTime.DateTime('%s/%0.2i/01 00:00 %s' % (tm.year(), month + 1, tz))




class ZScheduleEvent ( LogSupport ):
    """
    A schedule event, this wraps a callable with scheduling information

    Note that an event IS NOT scheduled on construction - it must be
    explicitly activated via editing it's status or calling manage_schedule
    """
    meta_type = portal_type = 'ZScheduleEvent'

    implements(IScheduleEvent)

    __ac_permissions__ = (
        (view, ('cronTab', 'expandedCronTab', 'active')),
        (view_management_screens, ('manage_scheduleForm', 'nextEventTime', 'event',
                                   'test_schedule')),
        (change_configuration, ('manage_editSchedule', 'manage_schedule',
                                'manage_unschedule',)),
        (execute_scheduler_events, ('manage_invokeEvent',)),
        ) + LogSupport.__ac_permissions__
    
    manage_options = (
        {'label':'Schedule', 'action':'manage_main', 'help':('ZScheduler', 'event.stx') },
        {'label':'Trigger', 'action':'manage_invokeEvent'},
        ) + LogSupport.manage_options
    
    last_executed = None

    manage_main = manage_scheduleForm = PageTemplateFile('zpt/event', globals())

    def __init__(self, id, title, callable, minute='*', hour='*', month='*', day_of_month='*', day_of_week='*', tz='UTC'):
        self.id = id
        self.title = title
        self.callable_id = callable
        self.minute = minute
        self.hour = hour
        self.month = month
        self.day_of_month = day_of_month
        self.day_of_week = day_of_week
        self.tz = tz
        self._active = 0
        self.time = DateTime.DateTime(0).toZone(self.tz)
        LogSupport.__init__(self)

    def nextEventTime(self, time=None):
        """
        return next executable time after given time
        """
	# hmmm - tz is a new parameter ...
	if not getattr(self, 'tz', None):
	    self.tz = 'UTC'
        
        if time is None:
            time = DateTime.DateTime(self.tz)

        # add one minute ...
        new_minute,increment_hr = get_time_for_spec('0-59', time.minute()+1, 0, 59)
        hour = int(time.hour())
        if increment_hr:
            hour += 1
        if hour == 24:
            my_time =  DateTime.DateTime('%s/%s/%s 00:%0.2i %s' % (
                time.year(), time.mm(), time.dd(), new_minute, time.timezone() ) ) + 1
        else:
            my_time = DateTime.DateTime('%s/%s/%s %0.2i:%0.2i %s' % (
                time.year(), time.mm(), time.dd(), hour, new_minute, time.timezone() ) )
                                                                                           
        while not self._matches(my_time):
            my_time = self._doMonth(self._doDay(self._doHour(self._doMinute(my_time))))

        return my_time

    def event(self):
        """
        return the actual event object/method

        the event object's security permissions control access
        """
        try:
            return self.aq_parent.restrictedTraverse(self.callable_id)
        except KeyError:
            # hmmm - must be a method ...
            return getattr(self, self.callable_id)

    def active(self):
        """
        active status flag
        """
        return getattr(aq_base(self), '_active', False)
    
    def timezones(self):
        """
        return known timezones
        """
        return DateTime.Timezones()
    
    def manage_beforeDelete(self, item, container):
        """
        delete event from scheduler, also must delete itself if the callable is deleted ...
        """
        self.getPhysicalRoot().ZSchedulerTool.unschedule(self)
        # this bit doesn't work ...
        if item.getId() == self.callable_id:
            container._delObject(self.getId())
                                 
    def manage_editSchedule(self, tz, minute, hour, month, day_of_month,
                            day_of_week, active=1, REQUEST=None):
        """
        update the schedule info ...
        """
        errors = []
        if not parse_spec(minute, 0, 59): errors.append( "Invalid Minute" )
        if not parse_spec(hour, 0, 23): errors.append( "Invalid Hour" )
        if not parse_spec(month, 1, 12): errors.append( "Invalid Month" )
        if not parse_spec(day_of_week, 0, 7): errors.append( "Invalid Day of Week" )
        if not parse_spec(day_of_month, 1, 31): errors.append( "Invalid Day of Month" )
        if ( minute == '*' and hour == '*' and month == '*' and \
                 day_of_week == '*' and day_of_month == '*'):
            errors.append("Cannot assign task to run every minute forever!")
        if errors:
            msg = string.join(errors, '\n')
            if REQUEST:
                REQUEST.set('manage_tabs_message', msg)
                REQUEST.set('management_view', 'Schedule')
                return self.manage_scheduleForm(self, REQUEST)
                            
            raise AssertionError, msg
        
        self.minute = minute
        self.hour = hour
        self.month = month
        self.day_of_month = day_of_month
        self.day_of_week = day_of_week
        self.tz = tz
        # time is actually calculable but we need it as an attribute to actually
        # index ourselves by it in the catalog ;)
        self.time = self.nextEventTime()
        self._active = active
        #
        # go place it in the schedule ...
        #
        if active:
            self.manage_schedule()
        else:
            self.manage_unschedule()

        if REQUEST:
            REQUEST.set('management_view', 'Schedule')
            return self.manage_scheduleForm(self,REQUEST)

    def manage_unschedule(self, REQUEST=None):
        """
        notify the scheduler
        """
        if self.active():
            self._active = 0
            self.getPhysicalRoot().ZSchedulerTool.unschedule(self)
        elif REQUEST:
            REQUEST.set('manage_tabs_message', 'Not active!')
        if REQUEST:
            REQUEST.set('management_view', 'Schedule')
            return self.manage_scheduleForm(self, REQUEST)
            
    def manage_schedule(self, REQUEST=None):
        """
        notify the scheduler
        """
        try:
	    self.getPhysicalRoot().ZSchedulerTool.unschedule(self)
        except:
            pass
        self.getPhysicalRoot().ZSchedulerTool.schedule(self)
        if REQUEST:
            REQUEST.set('management_view', 'Schedule')
            return self.manage_scheduleForm(self, REQUEST)
            
    def test_schedule(self, start_time=None, size=10):
        """
        visually display next scheduled times ...
        """
        if start_time is None:
            start_time = DateTime.DateTime(self.tz)

        if start_time.timezone() != self.tz:
            start_time = start_time.toZone(self.tz)

        results = []
        for index in range(0, size):
	    try:
                start_time = self.nextEventTime(start_time)
	    except:
		break
            results.append(start_time)
        return results
    
    def manage_repair(self, REQUEST=None):
        """ hmmm fix conversion of derived classes ..."""
        if not getattr(aq_base(self), 'callable_id', None):
            self.callable_id = self.id
        if not getattr(aq_base(self), 'log_batch_size', None):
            self.log_batch_size = 15
        if not getattr(aq_base(self), '_logger', None):
            self._logger = Logger()
        LogSupport.manage_repair(self)
        if REQUEST:
            REQUEST.set('management_view', 'Schedule')
            return self.manage_scheduleForm(self, REQUEST)

    def manage_invokeEvent(self, *args, **kw):
        """
        dispatch to callable and log any results
        """
        now = DateTime.DateTime(self.tz)
        output = self.event()(*args, **kw)
        self.log(self, 'executed...', output)
        self.last_executed = now
        self.time = self.nextEventTime(now)
        self.getPhysicalRoot().ZSchedulerTool.log(self, 'executed...', output)
        return output
        
    #
    # hmm productions go here ...
    #
    # each production modifies it's time parameter and returns a boolean saying
    # if it overflowed ie you should increment it's adjacent time component
    #

    def _matches(self, time):
	"""
	validity check the given DateTime against our spec
	"""
        day_ok = 1

        y = time.year()
        month_len = time._month_len[(y%4==0 and (y%100!=0 or y%400==0))][time.month()]

        if self.day_of_week != '*':
            day_ok = get_time_for_spec(self.day_of_week, time.dow(), 0, 7) == (time.dow(), 0)
            if self.day_of_month != '*' and not day_ok:            
                day_ok = get_time_for_spec(self.day_of_month, time.day(), 1, month_len) == (time.day(), 0)
        elif self.day_of_month != '*':
            day_ok = get_time_for_spec(self.day_of_month, time.day(), 1, month_len) == (time.day(), 0)

        return get_time_for_spec(self.minute, time.minute(), 0, 59) == (time.minute(), 0) and \
               get_time_for_spec(self.hour, time.hour(), 0, 23) == (time.hour(), 0) and \
               day_ok and get_time_for_spec(self.month, time.month(), 1, 12)

    def _doMinute(self, time):
        hour = int(time.hour())
        new_minute,increment_hr = get_time_for_spec(self.minute, time.minute(), 0, 59)
        if increment_hr:
            hour += 1
            if hour == 24:
                return  self._doMinute(DateTime.DateTime('%s/%s/%s 00:%0.2i %s' % (
                    time.year(), time.mm(), time.dd(), new_minute, self.tz ) ) + 1)
        return DateTime.DateTime('%s/%s/%s %0.2i:%0.2i %s' % (
            time.year(), time.mm(), time.dd(), hour, new_minute, self.tz ) )
                               

    def _doHour(self, time):
        hour = int(time.hour())
        day = time.day()
        new_hour,increment_day = get_time_for_spec(self.hour, hour, 0, 23)

        time = DateTime.DateTime('%s/%s/%s %0.2i:%s %s' % (
            time.year(), time.mm(), time.dd(), new_hour, time.minute(), self.tz
            ) )
        if increment_day:
            time += 1
        return time

    def _doDay(self, time):
        dom_time = dow_time = None
        if self.day_of_month != '*':
            dom_time = self._doDOM(time)

        if self.day_of_week != '*':
            dow_time = self._doDOW(time)

        if dom_time and dow_time:
            return min(dom_time, dow_time)

        return dom_time or dow_time or time
    
    def _doDOW(self, time):
        for x in range(0, 7):
            # if we didn't cycle thru the spec and still bound to ourself, then it's valid ...
            if get_time_for_spec(self.day_of_week, time.dow(), 0, 7) == (time.dow(), 0):
                return time
            time += 1 # increment by one day
        # eek should never get here ...
        raise AssertionError, "invalid day of week for %s (%s)" % (time, self.day_of_week) 

    def _doDOM(self, time):
        # dynamically calculate length of month
        y = time.year()
        month_len = time._month_len[(y%4==0 and (y%100!=0 or y%400==0))][time.month()]

        new_day,increment_mm = get_time_for_spec(self.day_of_month, time.day(), 1, month_len)

        if increment_mm:
            year = time.year()
            month = time.month()
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            if self.day_of_month == '*':
                time = DateTime.DateTime('%i/%0.2i/01 %0.2i:%0.2i %s' % (
                    year, month, time.hour(), time.minute(), self.tz
                    ) )
                return time

            time = DateTime.DateTime('%i/%0.2i/%0.2i %0.2i:%0.2i %s' % (
                year, month, int(get_first_time_for_spec(self.day_of_month, 1)),
                time.hour(), time.minute(), self.tz
                ) )
            return time

        time = DateTime.DateTime('%s/%0.2i/%0.2i %0.2i:%0.2i %s' % (
            time.year(), time.month(), new_day, time.hour(), time.minute(), self.tz ) )
        return time

    def _doMonth(self, time):
        year = time.year()
        new_month,increment_yr = get_time_for_spec(self.month, time.month(), 1, 12)
        if increment_yr: year+=1
        if new_month != time.month():
            dd = 1
        else:
            dd = time.dd()
        time = DateTime.DateTime('%s/%s/%s %0.2i:%0.2i %s' % (
            year, new_month, dd, time.hour(), time.minute(), self.tz ) )
        return time

    def cronTab(self):
        """
        crontab-formatted times
        """
        return ' '.join((self.minute, 
                         self.hour, 
                         self.day_of_month, 
                         self.month, 
                         self.day_of_week))

    def expandedCronTab(self):
        """
        cron time with ranges etc expanded into commas
        """
        return ' '.join((expand_spec(self.minute), 
                         expand_spec(self.hour), 
                         expand_spec(self.day_of_month), 
                         expand_spec(self.month),
                         expand_spec(self.day_of_week)))
        
AccessControl.class_init.InitializeClass( ZScheduleEvent )


manage_addZScheduleEventForm = PageTemplateFile('zpt/add_event', globals())
def manage_addZScheduleEvent(self, id, callable, title='', REQUEST=None):
    """
    Add an event to the schedule - you *MUST* actually edit the
    ZScheduleEvent to add it to the ZScheduler!
    """

    event = ZScheduleEvent(id, title or '-> %s' % callable, callable)

    self._setObject(id, event)

    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))

