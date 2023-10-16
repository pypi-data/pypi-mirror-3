# -*- coding: utf-8 -*-
'''
Created on Tue 16 Aug 2011

@author: leewei
'''
# ==============================================================================
# Copyright© 2011 LShift - Lee Wei <leewei@lshift.net>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from doctest  import DocTestSuite
from unittest import TestCase, makeSuite, TestSuite

from utility import *

try:
    from trac.perm import DefaultPermissionPolicy
except ImportError:
    DefaultPermissionPolicy = None

class TestHarnessTestCase(TestCase):
    """
        A test class to ensure test harness is working correctly.
    """

    ############################################################################
    # Setup #
    ############################################################################
    @classmethod
    def setUpClass(cls):
        """ Setup class for unittest. """

        do_init_setup_class(cls)

    @classmethod
    def tearDownClass(cls):
        """ Teardown class for unittest. """

        do_init_teardown_class(cls)

    def setUp(self):
        """ Setup method for unittest. """

        do_init_setup(self)

    def tearDown(self):
        """ Teardown method for unittest. """

        do_init_teardown(self)

    ############################################################################
    # Test Harness methods #
    ############################################################################
    def test_harness_create_tickets(self):
        """ >> TestHarness: Create random number of tickets (1-15) """

        num_tickets = self.test_harness.create_random_nonzero_tickets()
        self.assertEqual(num_tickets, self.test_harness._num_tix())

    def test_harness_delete_all_tickets(self):
        """ >> TestHarness: Create random tickets, then delete all """

        self.test_harness.create_random_nonzero_tickets()
        self.test_harness.tix_delete_all()
        self.assertEqual(0, self.test_harness._num_tix())

    def test_harness_set_estimatedtime(self):
        """ >> TestHarness: Create random tickets, estimatedtime(#1) = '64h' """

        self.test_harness.create_random_nonzero_tickets()
        self.assertNotEqual('64h', self.test_harness.tix_get_estimatedtime(1))
        self.test_harness.tix_set_estimatedtime(1, '64h')
        self.assertEqual('64h', self.test_harness.tix_get_estimatedtime(1))

def test_suite():
    suite = TestSuite()
    suite.addTest(DocTestSuite(TestHarness.__module__))
    suite.addTest(makeSuite(TestHarnessTestCase, 'test'))
    return suite
if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
