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
import random
import re
import png
import requests
from datetime import datetime, timedelta
from doctest  import DocTestSuite
from unittest import TestCase, makeSuite, TestSuite
from utility  import *
from customBurndownChart import BurndownChartEmbed
from genshi              import HTML
from genshi.builder      import tag
from genshi.core         import Stream, START, Attrs
from trac.resource       import ResourceNotFound
from trac.util.datefmt   import utc

SCRIPT_DIR = os.path.dirname(__file__)

def isAttrsEq(this, other):
    """ Compares whether 2 genshi.core.Attrs are structurally equivalent. """

    if not isinstance(this, Attrs) or not isinstance(other, Attrs):
        raise RuntimeError("Incorrect type supplied: != Attrs")

    if len(this) != len(other):
        return False

    diff = [ expected_key for (actual_key, _), (expected_key, _)
             in zip(this, other)
             if actual_key.replace('-class', 'class') !=
                expected_key.replace('-class', 'class')]

    return not diff
def isStreamEq(this, other):
    """ Compares 2 Genshi Streams for structural equivalence. """

    # extract structure
    this  = [ tag for (marker, tag, _) in this  if marker is START ]
    other = [ tag for (marker, tag, _) in other if marker is START ]
    if len(this) != len(other):
        return False
    # compare html tags
    diff = [ actual_elem
             for (actual_elem, actual_attrs), (expected_elem, expected_attrs)
             in zip(this, other)
             if (actual_elem != expected_elem)
             or (actual_elem == expected_elem
                 and not isAttrsEq(actual_attrs, expected_attrs))
    ]
    return not diff

class EmbedTestCase(TestCase):
    """
        A test class for the 'embed' module of the Trac Burndown chart plugin.
    """

    ############################################################################
    # Setup #
    ############################################################################
    @classmethod
    def setUpClass(cls):
        """ Setup class for unittest. """

        do_init_setup_class(cls)
        Stream.__eq__ = isStreamEq
        cls.embed = BurndownChartEmbed(cls.env)

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
    def create_milestone_if_not_exists(self, milestone_name):
        try:
            Milestone(self.env, milestone_name)
        except ResourceNotFound:
            test_milestone = Milestone(self.env)
            test_milestone.name = milestone_name
            test_milestone.due  = test_milestone.completed = datetime.now(utc)
            test_milestone.description = None
            test_milestone.insert()

    def test_milestone_has_hours(self):
        """ >> Embed::_milestone_has_hours(): test correctness of function """

        docstring = self.embed._milestone_has_hours.__doc__.strip()
        print '\n\t>', re.sub(r'\s{2,}', ' ', docstring)

        self.create_milestone_if_not_exists('Test Milestone')

        self.assertFalse(self.embed._milestone_has_hours('Test Milestone'))

        self.test_harness.tix_create(3, 'Test Milestone', [ 0, '0h', '0d' ])
        self.assertFalse(self.embed._milestone_has_hours('Test Milestone'))

        num_tickets = random.sample(range(64), 1)[0]
        self.test_harness.tix_create(num_tickets, 'Test Milestone', [1])
        self.assertTrue(self.embed._milestone_has_hours('Test Milestone'))

    def test_milestone_start_end_dates(self):
        """ >> Embed::_start_end_dates(): test correctness of function \
        (1 tix (-1w), 64 tix today, 1 tix (+1w)) """

        docstring = self.embed._start_end_dates.__doc__.strip()
        print '\n\t>', re.sub(r'\s{2,}', ' ', docstring)

        milestone_name = 'Test Milestone'
        self.create_milestone_if_not_exists(milestone_name)

        start_time = datetime.now(utc) - timedelta(weeks=53)
        self.test_harness.tix_create_single(
            {'milestone': milestone_name}, start_time)

        num_tickets = random.sample(range(64), 1)[0]
        self.test_harness.tix_create(num_tickets, milestone_name, [])

        end_time = datetime.now(utc) + timedelta(days=3)
        self.test_harness.tix_create_single(
            {'milestone': milestone_name}, end_time)

        self.assertItemsEqual([start_time, end_time],
            self.embed._start_end_dates(milestone_name))

    def test_create_burndown_chart_large_date_range_RTE(self):
        """ >> Embed::_create_burndown_chart(): range(dates) > (8w,1d) """

        milestone_name = 'Test Milestone'
        start_time = datetime.now(utc) - timedelta(weeks=53)
        end_time   = datetime.now(utc) + timedelta(days=3)

        with self.assertRaises(RuntimeError):
            self.embed._create_burndown_chart(
                [milestone_name, start_time, end_time, self.req])

    def create_burndown_chart(self):
        milestone_name = 'Test Milestone'
        start_time = datetime.now(utc) - timedelta(weeks=4)
        end_time   = datetime.now(utc) + timedelta(weeks=4)
        actual_stream = self.embed._create_burndown_chart(
            [milestone_name, start_time, end_time, self.req])
        return actual_stream

    def test_create_burndown_chart_html_structure(self):
        """ >> Embed::_create_burndown_chart(): verify output HTML structure """

        actual_stream = self.create_burndown_chart()
        expected_stream = \
            tag.div(_class='') \
                (tag.image(src='', alt='')) \
            .generate()

        self.assertTrue(actual_stream == expected_stream,
            'Error: generated BurndownChart HTML has incorrect structure')

    def test_create_burndown_chart_valid_image(self):
        """ >> Embed::_create_burndown_chart(): verify macro generates image """

        actual_stream = self.create_burndown_chart()
        img_url = actual_stream.select('image/@src') \
                    .render('html').replace('&amp;', '&')
        req = requests.get(img_url)
        self.assertEqual(200, req.status_code)

        r=png.Reader(bytes=req.content)
        width, height, pixels, metadata = r.read()
        w=png.Writer(width=width, height=height,
            alpha=metadata['alpha'],
            background=metadata['background'],
            bitdepth=metadata['bitdepth'],
            greyscale=metadata['greyscale'],
            interlace=metadata['interlace'],
            planes=metadata['planes'],
            size=metadata['size']
        )
        outfile = open(os.devnull, 'w')
        w.write(outfile, pixels)

    def test_filter_stream_invalid(self):
        """ >> Embed::filter_stream(): returns unhandled request unmodified """

        self.assertIsNone(
            self.embed.filter_stream(
                self.req, 'GET', 'roadmap_view.html', None, None
            )
        )

    def get_list_of_milestones_with_images(self, data={}):
        template_name = 'roadmap'
        html_file = open(
            os.path.join(SCRIPT_DIR, '%s.html'%template_name),
            'r')
        input_html = HTML(html_file.read())

        result = []
        for idx in xrange(1, len(self.milestones)+1):
            output_stream  = self.embed.filter_stream(
                self.req, 'GET', 'roadmap.html', input_html, data)
            output_stream = output_stream.select(
                '//div[@class="milestone"][%d]//image' % idx)
            images = [
                1 for (kind, item, _) in list(output_stream)
                if kind is START and item[0] == 'image'
            ]
            if len(images) > 0:
                result.append(idx)

        return result

    def test_roadmap_filter_nullTest(self):
        """ >> Embed::_do_roadmap_filter(): null data does not modify stream """

        self.test_harness.create_random_nonzero_tickets(
            ['milestone%d' % no for no in xrange(1, 5)])
        self.assertListEqual([], self.get_list_of_milestones_with_images())

    def test_roadmap_filter_display_charts_for_milestones(self):
        """ >> Embed::_do_roadmap_filter(): test correctness of function """

        self.test_harness.create_random_nonzero_tickets(
            ['milestone%d' % no for no in xrange(1, 5)])
        data = {
            'milestones': [
                Milestone(self.test_harness.env, 'milestone%d' % ms_no)
                for ms_no in [1, 3]
            ]
        }
        self.assertListEqual([1, 3],
            self.get_list_of_milestones_with_images(data))

    def xtest_roadmap_filter_hide_chart_for_empty_milestones(self):
        """ >> Embed::_do_roadmap_filter(): no change to empty milestones """

        self.test_harness.create_random_nonzero_tickets('milestone2')
        data = {
            'milestones': [
                Milestone(self.test_harness.env, 'milestone%d' % ms_no)
                for ms_no in [1, 3]
            ]
        }
        self.assertListEqual([],
            self.get_list_of_milestones_with_images(data))

    def get_images_from_milestone(self):
        """ runs through /milestone pipeline and returns detected images """

        template_name = 'milestone_view'
        html_file = open(os.path.join(SCRIPT_DIR, '%s.html' % template_name), 'r')
        input_html = HTML(html_file.read())
        output_stream = self.embed.filter_stream(
            self.req, 'GET', '%s.html' % template_name, input_html, {})
        output_stream = output_stream.select(
            '//div[@class="milestone"][1]//image')
        images = [
            1 for (kind, item, _) in list(output_stream)
            if kind is START and item[0] == 'image'
        ]

        return images

    def test_view_filter_no_tickets_no_chart(self):
        """ >> Embed::_do_view_filter(): no change to empty milestone """

        self.test_harness.create_random_nonzero_tickets([ 'milestone1', 'milestone3' ])
        self.req.args = { 'id': 'milestone2' }
        self.assertEqual(0, len(self.get_images_from_milestone()))

    def test_view_filter_yes_tickets_yes_chart(self):
        """ >> Embed::_do_view_filter(): chart shown for non-empty milestone """

        self.test_harness.create_random_nonzero_tickets([ 'milestone1', 'milestone3' ])
        self.req.args = { 'id': 'milestone1' }
        self.assertEqual(1, len(self.get_images_from_milestone()))

def test_suite():
    suite = TestSuite()
    suite.addTest(DocTestSuite(BurndownChartEmbed.__module__))
    suite.addTest(makeSuite(EmbedTestCase, 'test'))
    return suite
if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
