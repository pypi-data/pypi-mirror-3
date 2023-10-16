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
from unittest import TestCase, makeSuite, TestSuite
from doctest  import DocTestSuite
from utility  import *
from customBurndownChart.tooltip import BurndownChartToolTip

SCRIPT_DIR = os.path.dirname(__file__)

class TooltipTestCase(TestCase):
    """
        A test class for the 'tooltip' module of the Trac Burndown chart plugin.
    """

    ############################################################################
    # Setup #
    ############################################################################
    @classmethod
    def setUpClass(cls):
        """ Setup class for unittest. """

        do_init_setup_class(cls)
        cls.tooltip = BurndownChartToolTip(cls.env)

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
    def test_match_request_pass_paths(self):
        """ >> Tooltip::match_request(): test matching request paths """

        for path in [
                '/tooltip/tooltip.css', '/tooltip/tooltip.js',
                '/tooltip/qtip2.css',   '/tooltip/qtip2.js',
                '/jquery-1.6.4.min.js'
            ]:
            self.req.environ['PATH_INFO'] = path
            self.assertTrue(self.tooltip.match_request(self.req))

    def test_match_request_fail_paths(self):
        """ >> Tooltip::match_request(): test non-matching request paths """

        for path in [ 'tooltip.js', 'qtip2/qtip2.js', 'jquery-1.6.4.min.js' ]:
            self.req.environ['PATH_INFO'] = path
            self.assertFalse(self.tooltip.match_request(self.req))

    def test_process_request_tooltip_js(self):
        """ >> Tooltip::process_request(): test process request for tooltip.js """

        self.req.environ['PATH_INFO'] = '/tooltip/tooltip.js'
        template_name, data, content_type = self.tooltip.process_request(self.req)

        self.assertEqual('tooltip.html', template_name)
        self.assertDictEqual({}, data)
        self.assertEqual('text/javascript', content_type)

    def test_process_request_qtip_css(self):
        """ >> Tooltip::process_request(): test process request for qtip2.css """

        self.req.environ['PATH_INFO'] = '/tooltip/qtip2.css'
        self.tooltip.match_request(self.req)
        template_name, data, content_type = self.tooltip.process_request(self.req)

        self.assertEqual('css.html', template_name)

        self.assertIn('data', data)
        data = data['data']
        self.assertIn('css', data)

        self.assertEqual('text/css', content_type)

    def test_process_request_qtip_js(self):
        """ >> Tooltip::process_request(): test process request for qtip2.js """

        self.req.environ['PATH_INFO'] = '/tooltip/qtip2.js'
        self.tooltip.match_request(self.req)
        template_name, data, content_type = self.tooltip.process_request(self.req)

        self.assertEqual('js.html', template_name)

        self.assertIn('data', data)
        data = data['data']
        self.assertIn('js', data)

        self.assertEqual('text/javascript', content_type)

    def test_process_request_jQuery_js(self):
        """ >> Tooltip::process_request(): test process request for jQuery CDN """

        self.req.environ['PATH_INFO'] = '/jquery-1.6.4-latest.min.js'
        template_name, data, content_type = self.tooltip.process_request(self.req)
        self.assertEqual('js.html', template_name)
        self.assertIn('data', data)
        data = data['data']
        self.assertIn('js', data)
        self.assertIsNotNone(data['js'], 'Unable to load jQuery.js from CDN.')
        self.assertEqual('text/javascript', content_type)

    def test_pre_process_request(self):
        """ >> Tooltip::pre_process_request(): handler is not modified """

        self.assertIsNone(self.tooltip.pre_process_request(self.req, None))

    def do_post_process_request_common(self):
        """ post_process_request() test common method """

        self.req.chrome = { 'htdocs_location': '' }
        self.tooltip.post_process_request(self.req, None, None, None)

        if 'links' in self.req.chrome:
            self.assertListEqual([], getNotContainsInList(
                ['qtip2'],
                [item['href'] for item in self.req.chrome['links']['stylesheet']]
            ))

        if 'scripts' in self.req.chrome:
            self.assertListEqual([], getNotContainsInList(
                ['jquery', 'qtip2', 'tooltip'],
                [item['href'] for item in self.req.chrome['scripts']]
            ))

    def test_post_process_request_ticket(self):
        """ >> Tooltip::post_process_request(): css/js are added to request """

        self.req.environ['PATH_INFO'] = '/ticket/**'
        self.do_post_process_request_common()

    def test_post_process_request_newticket(self):
        """ >> Tooltip::post_process_request(): css/js are added to request """

        self.req.environ['PATH_INFO'] = '/newticket/2/*'
        self.do_post_process_request_common()

    def test_post_process_request_invalid(self):
        """ >> Tooltip::post_process_request(): request unchanged if invalid """

        self.req.environ['PATH_INFO'] = '/invalid/'
        self.do_post_process_request_common()

        self.assertNotIn('links', self.req.chrome)
        self.assertNotIn('scripts', self.req.chrome)

    def test_get_htdocs_dirs(self):
        """ >> Tooltip::get_htdocs_dirs(): tooltip tuple exists & path valid """

        dirs = self.tooltip.get_htdocs_dirs()
        self.assertIn('tooltip', [ key for (key, _) in dirs ])
        self.assertListEqual([True],
            [os.path.exists(path) for (key, path) in dirs if key == 'tooltip'])

    def test_get_templates_dirs(self):
        """ >> Tooltip::get_templates_dirs(): path exists """

        [dir] = self.tooltip.get_templates_dirs()
        self.assertTrue(os.path.exists(dir))

def test_suite():
    suite = TestSuite()
    suite.addTest(DocTestSuite(BurndownChartToolTip.__module__))
    suite.addTest(makeSuite(TooltipTestCase, 'test'))
    return suite
if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
