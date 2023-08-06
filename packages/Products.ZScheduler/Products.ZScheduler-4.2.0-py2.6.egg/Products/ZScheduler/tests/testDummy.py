#
# Skeleton ZopeTestCase
#
from Testing import ZopeTestCase

class TestDummy(ZopeTestCase.ZopeTestCase):

    def setUp(self):
	# runalltests gets confused ...
	pass

    def testImport(self):
        # check that it loads OK - we don't get to see normal import errors :(
        from Products.ZScheduler.timers.Dummy import Dummy


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDummy))
    return suite












