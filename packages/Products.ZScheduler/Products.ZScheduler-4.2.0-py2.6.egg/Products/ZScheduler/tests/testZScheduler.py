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

from Testing import ZopeTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase as ztc
#from Products.PloneTestCase.PloneTestCase import PloneTestCase as ztc
from Products.ZScheduler.ZScheduleEvent import ZScheduleEvent

ZopeTestCase.installProduct('ZScheduler')

# need to manually glue zcml as this isn't Plone/GS
from Products.Five import zcml, fiveconfigure

import Products.ZScheduler
zcml.load_config('configure.zcml', Products.ZScheduler)

class TestScheduler(ztc):

    def afterSetUp(self):

        portal = self.app
        #portal = self.portal
        portal._setObject('event1', ZScheduleEvent('event1', 'testing', 'no callable'))
        portal._setObject('event2', ZScheduleEvent('event2', 'testing', 'no callable'))
        portal._setObject('event3', ZScheduleEvent('event3', 'testing', 'no callable'))

        self.event1 = portal.event1

    def testSetup(self):
        self.failUnless('ZSchedulerTool' in self.app.objectIds())

    def testCatalog(self):
        zscheduler = self.app.ZSchedulerTool
        self.assertEqual(len(zscheduler.events()), 3)
        self.assertEqual(len(zscheduler.events(active=True)), 0)
        self.assertEqual(len(zscheduler.events(active=False)), 3)

        self.event1.manage_editSchedule('EST', '5', '*', '*', '*','*')
        self.assertEqual(len(zscheduler.events(active=True)), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestScheduler))
    return suite
