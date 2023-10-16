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
import re
from unittest import TestCase, makeSuite, TestSuite
from doctest  import DocTestSuite
from utility  import *
from genshi              import HTML
from genshi.builder      import tag
from genshi.core         import START
from customBurndownChart.inject import BurndownChart, UNIT
from urlparse            import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(__file__)

class InjectTestCase(TestCase):
    """
        A test class for the 'inject' module of the Trac Burndown chart plugin.
    """

    ############################################################################
    # Setup #
    ############################################################################
    @classmethod
    def setUpClass(cls):
        """ Setup class for unittest. """

        do_init_setup_class(cls)
        cls.inject = BurndownChart(cls.env)

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
    def test_cast_estimate_same_units_days(self):
        """ >> Inject::_cast_estimate(): estimates & units in days """

        self.inject._BurndownChart__display_unit = UNIT.days
        self.assertEqual(UNIT.days, self.inject._BurndownChart__display_unit)

        test_days = 1
        for case in [ '%d daYs ', '%dDAY', ' %dd' ]:
            self.assertEqual(test_days,
                self.inject._cast_estimate(case % test_days))

    def test_cast_estimate_same_units_hours(self):
        """ >> Inject::_cast_estimate(): estimates & units in hours """

        self.inject._BurndownChart__display_unit = UNIT.hours
        self.assertEqual(UNIT.hours, self.inject._BurndownChart__display_unit)

        test_hours = 1
        for case in [ '%dHOURS', ' %d hOuR', '%d H ' ]:
            self.assertEqual(test_hours,
                self.inject._cast_estimate(case % test_hours))

    def test_cast_estimate_different_units_days(self):
        """ >> Inject::_cast_estimate(): estimates in hours; units in days """

        self.inject._BurndownChart__display_unit = UNIT.days
        self.assertEqual(UNIT.days, self.inject._BurndownChart__display_unit)

        self.env.config.set('estimation-tools', 'daily_work_hours', 9)
        work_hours = int(self.inject._BurndownChart__work_hours)

        test_hours = 60
        for case in [ '%dhours', ' %d hour', '%d h ' ]:
            self.assertEqual(test_hours/work_hours,
                self.inject._cast_estimate(case % test_hours))

    def test_cast_estimate_different_units_hours(self):
        """ >> Inject::_cast_estimate(): estimates in days; units in hours """

        self.inject._BurndownChart__display_unit = UNIT.hours
        self.assertEqual(UNIT.hours, self.inject._BurndownChart__display_unit)

        self.env.config.set('estimation-tools', 'daily_work_hours', 9)
        work_hours = int(self.inject._BurndownChart__work_hours)

        test_days = 1
        for case in [ '%d days ', '%dday', ' %dd' ]:
            self.assertEqual(test_days * work_hours,
                self.inject._cast_estimate(case % test_days))

    def test_expand_macro_exactly_two_charts_present(self):
        """ >> Inject::expand_macro(): 2 charts present for units h/d """

        html = self.inject.expand_macro(
            self.formatter, '', 'startdate=2011-09-01').generate()
        self.assertEqual(2,
            len([ 1 for (kind, _, _) in list(html.select('//image'))
                  if kind is START ]))

    def test_bdc_squirt_markup_exactly_two_charts_present(self):
        """ >> Inject::_bdc_squirt_markup(): 2 charts present for units h/d """

        html = self.inject._bdc_squirt_markup(tag.image(), tag.image()) \
                .generate()
        self.assertEqual(2,
            len([ 1 for (kind, _, _) in list(html.select('//image'))
                  if kind is START ]))

    def test_bdc_squirt_markup_zoom_buttons_present(self):
        """ >> Inject::_bdc_squirt_markup(): zoom panel + buttons present """

        html = self.inject._bdc_squirt_markup('', tag.div()).generate()
        classes = \
            [ self.inject._BurndownChart__prop[elem]['class']
                for elem in [ 'zoompanel', 'zoomout', 'zoomin' ] ]
        copy = html.render('html')
        found = 0
        for item in classes:
            fragment = HTML(copy).select('//*[@class="%s"]' % item)
            for (kind, data, _) in list(fragment):
                if kind is START:
                    _, attrs = data
                    if 'class' in attrs:
                        elemClass = attrs.get('class')
                        if elemClass == item:
                            found += 1
                            continue
        self.assertEqual(len(classes), found)

    def test_bdc_squirt_markup_initial_view_present(self):
        """ >> Inject::_bdc_squirt_markup(): initial display units specified """

        html = self.inject._bdc_squirt_markup('', tag.div()).generate()
        self.assertEqual(1,
            len([ 1 for (kind, _, _)
                  in list(html.select('//input[@id="resolution"]'))
                  if kind is START ]))

    def test_bdc_squirt_markup_chart_displayed_consistent_with_units(self):
        """ >> Inject::_bdc_squirt_markup(): chart in right units shown first """

        html = self.inject._bdc_squirt_markup(
            tag.image(id='hours'), tag.image(id='days')) \
            .generate()
        copy = html.render('html')
        initial_view = HTML(copy).select('//input[@id="resolution"]/@value')

        # assumes only one of each chart is present (validated previously)
        self.assertNotIn('display:none',
            re.sub('\s', '',
                HTML(copy).select('//image[@id="%s"]/@style' % initial_view)
            .render('html')))
        self.assertIn('display:none',
            re.sub('\s', '',
                HTML(copy).select('//image[@id!="%s"]/@style' % initial_view)
            .render('html')))

    def test_bdc_construct_nullTest(self):
        """ >> Inject::_bdc_construct(): null attributes supplied """

        self.assertIsNotNone(
            self.inject._bdc_construct('id', tag.image(src=''), None, None)
        )

    def test_bdc_construct_replace_attributes(self):
        """ >> Inject::_bdc_construct(): attributes are replaced in query """

        REPLACE_TEXT = '<REPLACE>'
        test_image = tag.image(src='http://chart.apis.google.com/chart?chxt=x%2Cx%2Cy&chxr=2%2C0%2C100&chco=ff9900%2Cffddaa&chtt=None&chxl=0%3A%7C1%7C2%7C3%7C4%7C5%7C6%7C7%7C8%7C9%7C10%7C11%7C12%7C13%7C14%7C15%7C1%3A%7C9%2F2011%7C9%2F2011&chd=t%3A0.00%2C7.14%2C14.29%2C21.43%2C28.57%2C35.71%2C42.86%2C50.00%2C57.14%2C64.29%2C71.43%2C78.57%2C85.71%2C92.86%2C100.00%7C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00&chf=c%2Cs%2Cffffff00%7Cbg%2Cs%2C00000000&chg=100.0%2C100.0%2C1%2C0&chm=R%2Cccccccaa%2C0%2C0.10%2C0.25%7CR%2Cccccccaa%2C0%2C0.60%2C0.75&chs=800x200&cht=lxy')
        output_image = self.inject._bdc_construct('id', test_image,
            { 'chs': REPLACE_TEXT, 'cht': REPLACE_TEXT }, None)

        _, _, _, _, query, _ = urlparse(output_image.attrib.get(u'src'))
        qsdata = parse_qs(query)

        for change in [ 'cht', 'chs' ]:
            self.assertIn(change, qsdata)
            self.assertListEqual([REPLACE_TEXT], qsdata[change])

    def test_bdc_construct_extend_attributes(self):
        """ >> Inject::_bdc_construct(): attributes are extended in query """

        EXTEND_TEXT = '<EXTEND>'
        test_image = tag.image(src='http://chart.apis.google.com/chart?chxt=x%2Cx%2Cy&chxr=2%2C0%2C100&chco=ff9900%2Cffddaa&chtt=None&chxl=0%3A%7C1%7C2%7C3%7C4%7C5%7C6%7C7%7C8%7C9%7C10%7C11%7C12%7C13%7C14%7C15%7C1%3A%7C9%2F2011%7C9%2F2011&chd=t%3A0.00%2C7.14%2C14.29%2C21.43%2C28.57%2C35.71%2C42.86%2C50.00%2C57.14%2C64.29%2C71.43%2C78.57%2C85.71%2C92.86%2C100.00%7C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00%2C0.00&chf=c%2Cs%2Cffffff00%7Cbg%2Cs%2C00000000&chg=100.0%2C100.0%2C1%2C0&chm=R%2Cccccccaa%2C0%2C0.10%2C0.25%7CR%2Cccccccaa%2C0%2C0.60%2C0.75&chs=800x200&cht=lxy')
        output_image = self.inject._bdc_construct('id', test_image,
            None, { 'chs': EXTEND_TEXT, 'cht': EXTEND_TEXT })

        _, _, _, _, query, _ = urlparse(output_image.attrib.get(u'src'))
        qsdata = parse_qs(query)

        for key, value in [ ('chs', '800x200'), ('cht', 'lxy') ]:
            self.assertIn(key, qsdata)
            self.assertListEqual(['%s%s' % (value, EXTEND_TEXT)], qsdata[key])

    def test_match_request_pass_paths(self):
        """ >> Inject::match_request(): test matching request paths """

        for path in [ '/inject/inject.js', '/jquery-1.6.4.min.js' ]:
            self.req.environ['PATH_INFO'] = path
            self.assertTrue(self.inject.match_request(self.req))

    def test_match_request_fail_paths(self):
        """ >> Inject::match_request(): test non-matching request paths """

        for path in [ 'inject.js', 'inject/inject.js', 'jquery-1.6.4.min.js' ]:
            self.req.environ['PATH_INFO'] = path
            self.assertFalse(self.inject.match_request(self.req))

    def test_process_request_inject_js(self):
        """ >> Inject::process_request(): test process request for inject.js """

        self.req.environ['PATH_INFO'] = '/inject/inject.js'
        template_name, data, content_type = self.inject.process_request(self.req)
        self.assertEqual('inject.html', template_name)
        self.assertIn('data', data)
        data = data['data']
        self.assertItemsEqual(['zoompanel', 'chart', 'container'], data.keys())
        self.assertEqual('text/javascript', content_type)

    def test_process_request_jQuery_js(self):
        """ >> Inject::process_request(): test process request for jQuery CDN """

        self.req.environ['PATH_INFO'] = '/jquery-1.6.4-latest.min.js'
        template_name, data, content_type = self.inject.process_request(self.req)
        self.assertEqual('js.html', template_name)
        self.assertIn('data', data)
        data = data['data']
        self.assertIn('js', data)
        self.assertIsNotNone(data['js'], 'Unable to load jQuery.js from CDN.')
        self.assertEqual('text/javascript', content_type)

    def test_pre_process_request(self):
        """ >> Inject::pre_process_request(): handler is not modified """

        self.assertIsNone(self.inject.pre_process_request(self.req, None))

    def do_post_process_request_common(self):
        """ post_process_request() test common method """

        self.req.chrome = { 'htdocs_location': '' }
        self.inject.post_process_request(self.req, None, None, None)

        if 'links' in self.req.chrome:
            self.assertListEqual([], getNotContainsInList(
                ['burndownchart', 'jquery-ui'],
                [item['href'] for item in self.req.chrome['links']['stylesheet']]
            ))

        if 'scripts' in self.req.chrome:
            self.assertListEqual([], getNotContainsInList(
                ['preload', 'jquery', 'jquery-ui', 'inject'],
                [item['href'] for item in self.req.chrome['scripts']]
            ))

    def test_post_process_request_roadmap(self):
        """ >> Inject::post_process_request(): css/js are added to request """

        self.req.environ['PATH_INFO'] = '/roadmap/**'
        self.do_post_process_request_common()

    def test_post_process_request_milestone(self):
        """ >> Inject::post_process_request(): css/js are added to request """

        self.req.environ['PATH_INFO'] = '/milestone/2/*'
        self.do_post_process_request_common()

    def test_post_process_request_invalid(self):
        """ >> Inject::post_process_request(): request unchanged if invalid """

        self.req.environ['PATH_INFO'] = '/invalid/'
        self.do_post_process_request_common()

        self.assertNotIn('links', self.req.chrome)
        self.assertNotIn('scripts', self.req.chrome)

    def test_get_htdocs_dirs(self):
        """ >> Inject::get_htdocs_dirs(): inject tuple exists & path valid """

        dirs = self.inject.get_htdocs_dirs()
        self.assertIn('inject', [ key for (key, _) in dirs ])
        self.assertListEqual([True],
            [os.path.exists(path) for (key, path) in dirs if key == 'inject'])

    def test_get_templates_dirs(self):
        """ >> Inject::get_templates_dirs(): path exists """

        [dir] = self.inject.get_templates_dirs()
        self.assertTrue(os.path.exists(dir))

def test_suite():
    suite = TestSuite()

    suite.addTest(DocTestSuite(BurndownChart.__module__))
    suite.addTest(makeSuite(InjectTestCase, 'test'))

    return suite

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
