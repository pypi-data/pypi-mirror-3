#
#    Copyright (C) 2011-2012  Corporation of Balclutha. All rights Reserved.
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
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.ZScheduler.config import TOOLNAME
ztc.installProduct('ZScheduler')
ptc.setupPloneSite(products=['ZScheduler'])


class TestTool(ptc.PloneTestCase):

    def testSetup(self):
        #self.assertEqual(self.portal.objectIds(), None)
        self.failUnless(TOOLNAME in self.portal.objectIds())

        # make sure ZSchedulerTool set up in root
        self.failUnless('ZSchedulerTool' in self.portal.getPhysicalRoot().objectIds())

    def testQueue(self):
        tool = getattr(self.portal, TOOLNAME)
        self.assertEqual(tool.queueValues(), [])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTool))
    return suite
