#
#    Copyright (C) 2005-2011  Corporation of Balclutha. All rights Reserved.
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

import os

from Testing import ZopeTestCase
ZopeTestCase.installProduct('ZScheduler')

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = os.path.abspath(curdir)
else:
    # Test was called by another test.
    _prefix = os.path.abspath(os.path.dirname(__file__))


class TestFSScheduleEvent(ZopeTestCase.ZopeTestCase):

    def _makeOne( self, id, filename='event.sched'):

        from Products.ZScheduler.FSZScheduleEvent import FSZScheduleEvent

        return FSZScheduleEvent( id, os.path.join(_prefix, filename) )

    def _extractFile( self ):

        path = os.path.join(_prefix, 'event.sched')
        f = open( path, 'rb' )
        try:
            data = f.read()
        finally:
            f.close()

        return path, data

    def test_ctor( self ):

        path, ref = self._extractFile()

        event = self._makeOne( 'test_file')

        self.assertEqual(event.day_of_month, '*' )
        self.assertEqual(event.day_of_week, '*' )
        self.assertEqual(event.hour, '1' )
        self.assertEqual(event.minute, '1' )
        self.assertEqual(event.month, '3,6,9,12' )
        self.assertEqual(event.tz, 'EADT' )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFSScheduleEvent))
    return suite










