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


from Testing import ZopeTestCase
from Products.ZScheduler.ZScheduleEvent import *
from DateTime import DateTime

ZopeTestCase.installProduct('ZScheduler')



class TestScheduleEvent(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.event = ZScheduleEvent('test', 'testing', 'no callable')
        self.now = DateTime('Jan 1 2004 00:00:00 UTC')

    def testRangeExpansions(self):
        self.assertEqual(get_time_for_spec('*', 5, 0, 59), (5,0))
        self.assertEqual(get_time_for_spec('5', 5, 0, 59), (5,0))
        self.assertEqual(get_time_for_spec('5', 6, 0, 59), (5,1))
        self.assertEqual(get_time_for_spec('1-5', 5, 0, 59), (5,0))
        self.assertEqual(get_time_for_spec('1,3,5', 5, 0, 59), (5,0))
        self.assertEqual(get_time_for_spec('1,3,5-20', 5, 0, 59), (5,0))
        self.assertEqual(get_time_for_spec('1,3', 5, 1, 12), (1,1))

    def testIntervalExpansion(self):
        self.assertEqual(expand_spec('1-5'), '1,2,3,4,5')

    def testSkipsExpansion(self):
        self.assertEqual(expand_spec('10-30/5'), '10,15,20,25,30')

    def testRangesExpansion(self):
        self.assertEqual(expand_spec('1-2,10-12'), '1,2,10,11,12')

    def testNextDay(self):
        self.assertEqual(next_day(DateTime('2004/01/01'), 'UTC'), DateTime('2004/01/02 UTC'))
        self.assertEqual(next_day(DateTime('2004/01/31'), 'UTC'), DateTime('2004/02/01 UTC'))
        self.assertEqual(next_day(DateTime('2004/12/31'), 'UTC'), DateTime('2005/01/01 UTC'))

    def testNextMonth(self):
        self.assertEqual(next_month(DateTime('2004/01/01'), 'UTC'), DateTime('2004/02/01 UTC'))
        self.assertEqual(next_month(DateTime('2004/01/31'), 'UTC'), DateTime('2004/02/01 UTC'))
        self.assertEqual(next_month(DateTime('2004/12/31'), 'UTC'), DateTime('2005/01/01 UTC'))
        
    def testMinute(self):
        self.event.manage_editSchedule('US/Eastern', '1', '*', '*', '*', '*', 0)
        # note tz difference with now in UTC ...
        self.assertEqual(self.event.test_schedule(self.now, 5),
                         [ DateTime('Dec 31 2003 19:01:00 US/Eastern'),
                           DateTime('Dec 31 2003 20:01:00 US/Eastern'),
                           DateTime('Dec 31 2003 21:01:00 US/Eastern'),
                           DateTime('Dec 31 2003 22:01:00 US/Eastern'),
                           DateTime('Dec 31 2003 23:01:00 US/Eastern') ])
    def testHour(self):
        self.event.manage_editSchedule('US/Eastern', '1', '1-2', '*', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(self.now, 5),
                         [ DateTime('Jan 1 2004 01:01:00 US/Eastern'),
                           DateTime('Jan 1 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 2 2004 01:01:00 US/Eastern'),
                           DateTime('Jan 2 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2004 01:01:00 US/Eastern') ])

    def testMonth(self):
        self.event.manage_editSchedule('US/Eastern', '1', '1', '11,12', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(self.now, 5),
                         [ DateTime('Nov 1 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 2 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 3 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 4 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 5 2004 01:01:00 US/Eastern') ])

    def testDayOfMonth(self):
        self.event.manage_editSchedule('US/Eastern', '1', '1', '11', '3,11', '*', 0)
        self.assertEqual(self.event.test_schedule(self.now, 6),
                         [ DateTime('Nov  3 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 11 2004 01:01:00 US/Eastern'),
                           DateTime('Nov  3 2005 01:01:00 US/Eastern'),
                           DateTime('Nov 11 2005 01:01:00 US/Eastern'),
                           DateTime('Nov  3 2006 01:01:00 US/Eastern'),
                           DateTime('Nov 11 2006 01:01:00 US/Eastern') ])
    def testDayOfWeek(self):
        self.event.manage_editSchedule('US/Eastern', '1', '1', '11', '*', '2', 0)
        self.assertEqual(self.event.test_schedule(self.now, 6),
                         [ DateTime('Nov  2 2004 01:01:00 US/Eastern'),
                           DateTime('Nov  9 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 16 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 23 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 30 2004 01:01:00 US/Eastern'),
                           DateTime('Nov  1 2005 01:01:00 US/Eastern') ])

    def testDOWandMonth(self):
        self.event.manage_editSchedule('US/Eastern', '1', '1', '11', '3,11', '2', 0)
        self.assertEqual(self.event.test_schedule(self.now, 6),
                         [ DateTime('Nov  2 2004 01:01:00 US/Eastern'),
                           DateTime('Nov  3 2004 01:01:00 US/Eastern'),
                           DateTime('Nov  9 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 11 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 16 2004 01:01:00 US/Eastern'),
                           DateTime('Nov 23 2004 01:01:00 US/Eastern'), ])

    def testIntraDay(self):
        self.event.manage_editSchedule('US/Eastern', '1-2,31-32', '1', '*', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(DateTime('Jan 01 2004 1:24 US/Eastern'), 5),
                         [ DateTime('Jan 1 2004 01:31:00 US/Eastern'),
                           DateTime('Jan 1 2004 01:32:00 US/Eastern'),
                           DateTime('Jan 2 2004 01:01:00 US/Eastern'),
                           DateTime('Jan 2 2004 01:02:00 US/Eastern'),
                           DateTime('Jan 2 2004 01:31:00 US/Eastern'), ])
        
    def testMinuteOverflow(self):
        self.event.manage_editSchedule('US/Eastern', '0-2,59', '1,2', '*', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(DateTime('Jan 01 2004 1:24 US/Eastern'), 5),
                         [ DateTime('Jan 1 2004 01:59:00 US/Eastern'),
                           DateTime('Jan 1 2004 02:00:00 US/Eastern'),
                           DateTime('Jan 1 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 1 2004 02:02:00 US/Eastern'),
                           DateTime('Jan 1 2004 02:59:00 US/Eastern'), ])
        #
        # this tests a screwed time rollover at Enchant ...
        #
        self.event.manage_editSchedule('UTC', '1', '1', '*', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(DateTime('Jan 01 2004 23:24 UTC'), 5),
                         [ DateTime('Jan 2 2004 01:01:00 UTC'),
                           DateTime('Jan 3 2004 01:01:00 UTC'),
                           DateTime('Jan 4 2004 01:01:00 UTC'),
                           DateTime('Jan 5 2004 01:01:00 UTC'),
                           DateTime('Jan 6 2004 01:01:00 UTC'), ])

    
    def testHourOverflow(self):
        self.event.manage_editSchedule('US/Eastern', '1', '2', '1', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(DateTime('Jan 02 2004 1:24 US/Eastern'), 5),
                         [ DateTime('Jan 2 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 4 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 5 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 6 2004 02:01:00 US/Eastern'), ])
    
    def testDayOverflow(self):
        self.event.manage_editSchedule('US/Eastern', '1', '2', '1', '3', '*', 0)
        self.assertEqual(self.event.test_schedule(DateTime('Jan 02 2004 1:24 US/Eastern'), 5),
                         [ DateTime('Jan 3 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2005 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2006 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2007 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2008 02:01:00 US/Eastern'), ])

    def testTimeZone(self):
        # dunno about this - timezone's seem f**ked to me ...
        tm = self.now.toZone('UTC')
        self.event.manage_editSchedule('US/Eastern', '1', '2', '1', '3', '*', 0)
        self.assertEqual(self.event.test_schedule(tm, 5),
                         [ DateTime('Jan 3 2004 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2005 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2006 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2007 02:01:00 US/Eastern'),
                           DateTime('Jan 3 2008 02:01:00 US/Eastern'), ])

    def testRollOverDay(self):
        tm = DateTime('2004/09/12 23:57 UTC')
        self.event.manage_editSchedule('UTC', '0-59', '23,0', '*', '*', '*', 0)
        self.assertEqual(self.event.test_schedule(tm, 5),
                         [ DateTime('2004/09/12 23:58 UTC'),
                           DateTime('2004/09/12 23:59 UTC'),
                           DateTime('2004/09/13 00:00 UTC'),
                           DateTime('2004/09/13 00:01 UTC'),
                           DateTime('2004/09/13 00:02 UTC'),
                           ])

    def testCronStrs(self):
        self.event.manage_editSchedule('UTC', '0-59/10', '23,0', '1-5', '*', '*', 0)
        self.assertEqual(self.event.cronTab(), '0-59/10 23,0 * 1-5 *')
        self.assertEqual(self.event.expandedCronTab(), '0,10,20,30,40,50 23,0 * 1,2,3,4,5 *')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestScheduleEvent))
    return suite
