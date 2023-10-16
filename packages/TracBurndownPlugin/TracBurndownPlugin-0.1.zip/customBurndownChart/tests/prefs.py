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

import os
from unittest         import TestCase, makeSuite, TestSuite
from doctest          import DocTestSuite
from trac.perm        import PermissionError
from trac.web.session import Session
from trac.web.api     import RequestDone
from utility          import *
from customBurndownChart.prefs import BurndownChartAdminPanel
try:
    from trac.perm import DefaultPermissionPolicy
except ImportError:
    DefaultPermissionPolicy = None

SCRIPT_DIR = os.path.dirname(__file__)

class PrefsTestCase(TestCase):
    """
        A test class for the 'prefs' module of the Trac Burndown chart plugin.
    """

    ############################################################################
    # Setup #
    ############################################################################
    @classmethod
    def setUpClass(cls):
        """ Setup class for unittest. """

        do_init_setup_class(cls)
        cls.prefs = BurndownChartAdminPanel(cls.env)

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
    # Unit tests #
    ############################################################################
    def test_get_admin_panels_unauthorised(self):
        """ >> Prefs::get_admin_panels(): hide option if insufficient privileges """

        self.assertRaises(StopIteration,
            self.prefs.get_admin_panels(self.req).next)

    def test_get_admin_panels_admin(self):
        """ >> Prefs::get_admin_panels(): TRAC_ADMIN => show admin option """

        # set permission
        PermissionSystem(self.env).grant_permission('lshift', 'TRAC_ADMIN')

        self.assertIsInstance(
            self.prefs.get_admin_panels(self.req).next(), tuple)

    def test_render_admin_panels_unauthorised(self):
        """ >> Prefs::render_admin_panels(): non-admin raises PermissionError """

        self.assertRaises(PermissionError,
            self.prefs.render_admin_panel, self.req, None, None, None)

    def test_render_admin_panels_admin_get(self):
        """ >> Prefs::render_admin_panels(): display admin panel (HTTP GET) """

        # set permission
        PermissionSystem(self.env).grant_permission('lshift', 'TRAC_ADMIN')

        self.assertIsInstance(
            self.prefs.render_admin_panel(self.req, None, None, None), tuple)

    def test_render_admin_panels_admin_post(self):
        """ >> Prefs::render_admin_panels(): display admin panel (HTTP POST) """

        self.req.environ['REQUEST_METHOD'] = 'POST'
        self.req.session = Session(self.env, self.req)

        # set permission
        PermissionSystem(self.env).grant_permission('lshift', 'TRAC_ADMIN')

        self.assertRaises(RequestDone,
            self.prefs.render_admin_panel, self.req, None, 'burndownchart', None
        )

    def test_get_htdocs_dirs(self):
        """ >> Prefs::get_htdocs_dirs(): prefs tuple exists & path valid """

        dirs = self.prefs.get_htdocs_dirs()
        self.assertIn('prefs', [ key for (key, _) in dirs ])
        self.assertListEqual([True],
            [os.path.exists(path) for (key, path) in dirs if key == 'prefs'])

    def test_get_templates_dirs(self):
        """ >> Prefs::get_templates_dirs(): path exists """

        [dir] = self.prefs.get_templates_dirs()
        self.assertTrue(os.path.exists(dir))

def test_suite():
    suite = TestSuite()
    suite.addTest(DocTestSuite(BurndownChartAdminPanel.__module__))
    suite.addTest(makeSuite(PrefsTestCase, 'test'))
    return suite
if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
