#
# Skeleton ZopeTestCase
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

class TestDummy(ZopeTestCase.ZopeTestCase):

    def setUp(self):
	# runalltests gets confused ...
	pass

    def testImport(self):
        # check that it loads OK - we don't get to see normal import errors :(
        from Products.ZScheduler.timers.Dummy import Dummy


if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestDummy))
        return suite












