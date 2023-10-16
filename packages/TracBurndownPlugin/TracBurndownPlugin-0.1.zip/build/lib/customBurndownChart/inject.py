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

from __future__       import with_statement
import os
import re
import urllib
import urllib2
from config           import *
from copy             import copy
from urlparse         import urlparse, urlunparse, parse_qs
from genshi.builder   import tag
from trac.core        import *
from trac.config      import Option
from estimationtools.burndownchart import BurndownChart
from estimationtools.utils import parse_options
from pkg_resources    import resource_filename
from trac.web         import IRequestHandler, IRequestFilter
from trac.web.chrome  import ITemplateProvider, add_stylesheet, add_script, \
                             add_script_data

class Enum(set):
    """
        Tiny implementation of an enumeration class for displaying charts in
        hours/days.
    """

    def __getattr__(self, name):
        name = name.lower()
        if name in self:
            return name
        raise AttributeError("no such Enum(%(name)s) found." % locals())

UNIT = Enum(["days", "hours"])

class BurndownChart(BurndownChart):
    """
        Base class to inject additional custom functionality after
        the embedded macros '[[BurndownChart(...)]]' are expanded,
        eg. zoom buttons, layout styles etc.
    """
    implements(IRequestHandler, IRequestFilter, ITemplateProvider)

    __prop = {
      "zoompanel": { "class": "zoompanel" }
    , "zoomout":   {
            "class": "ui-icon ui-icon-circle-minus zoombutton btn-zoom-out"
        }
    , "zoomin":    {
            "class": "ui-icon ui-icon-circle-plus zoombutton btn-zoom-in"
        }
    , "container":     { "class": "bdc_container"           }
    , "burndownchart": { "class": "bdc_img", "id": "bdc_%s" }
    }

    # options will be populated with values outside of methods (within class)
    __work_hours = Option('estimation-tools', 'daily_work_hours', 8, doc=\
        """Specifies the number of working hours in a day for burndown charts.
        Defaults to 8""")

    __display_unit = DEFAULT_CHART_DISPLAY['unit']

    def _cast_estimate(self, estimate):
        """ Converts estimatedtime units from/to days/hours as appropriate. """

        # split numeric, unit components of estimate, ie. {1,'d'} from '1d'
        # also accepts floating point, eg. '1.5 h'
        _, number, unit, _ = \
            re.split(r'^([\d.]+)\s*(\w+)$', str(estimate).strip().lower())
        estimate = float(number)

        # scale estimate value to days/hours for chart y-axis for differing units
        # allows working hours/day to be floating point
        if self.__display_unit == UNIT.hours and unit in ['days', 'day', 'd']:
            estimate *= float(self.__work_hours)
        elif self.__display_unit == UNIT.days \
                and unit in ['hours', 'hour', 'h', '']:
            estimate /= float(self.__work_hours)

        return super(BurndownChart, self)._cast_estimate(estimate)

    ############################################################################
    # WikiMacroBase > EstimationToolsBase methods #
    ############################################################################
    def expand_macro(self, formatter, name, content):
        """
            Enriches macro expansion from EstimationTools to include hours/days
            in query string submitted to Google's Chart API.

            Generates 2 copies of charts (for units in hours & days).
        """

        # save state
        current_display_unit = self.__display_unit

        self.__display_unit = UNIT.hours
        # leverage generated output from existing estimationtoolsplugin
        bdc_markup = \
            super(BurndownChart, self).expand_macro(formatter, name, content)
        bdc_hours = self._bdc_construct(UNIT.hours, bdc_markup,
            {"chxt": u'x,x,y,y'}, {"chxl": u'|3:||Hours'})

        self.__display_unit = UNIT.days
        # leverage generated output from existing estimationtoolsplugin
        bdc_markup = \
            super(BurndownChart, self).expand_macro(formatter, name, content)
        bdc_days = self._bdc_construct(UNIT.days, bdc_markup,
            {"chxt": u'x,x,y,y'},
            {"chxl": u'|3:||Days (%sh/day)' % self.__work_hours})

        # restore state
        self.__display_unit = current_display_unit

        # generate html output
        return self._bdc_squirt_markup(bdc_hours, bdc_days)

    def _bdc_squirt_markup(self, bdc_hours, bdc_days):
        result = \
          tag.input(type="hidden", id="resolution", value=self.__display_unit) \
        + tag.div(class_=self.__prop["zoompanel"]["class"])( \
            tag.a(href="#")(tag.span(class_=self.__prop["zoomout"]["class"])) \
          + tag.a(href="#")(tag.span(class_=self.__prop["zoomin"]["class"]))  \
          ) \
        + tag(bdc_hours) \
        + tag(bdc_days(style="display:none;"))

        return result

    def _bdc_construct(self, id, original, attr_replace, attr_extend):
        """ Returns a copy of the Burndown chart with additional attributes. """

        # 1. unpack attributes
        scheme, netloc, path, params, query, fragment = \
            urlparse(original.attrib.get(u'src'))
        qsdata = parse_qs(query) # uniq dict key; val = list(items)

        # 2. enhance attributes
        if attr_replace:
            for key, value in attr_replace.iteritems():
                qsdata[key] = value

        if attr_extend:
            for key, value in attr_extend.iteritems():
                qsdata[key] = ''.join([''.join(qsdata[key]), value])

        # 3. repack attributes into query string
        query = '&'.join(['='.join([key, urllib.quote(''.join(value))]) \
            for key, value in qsdata.items()])
        src = urlunparse((scheme, netloc, path, params, query, fragment))

        # 4. generate new Markup stream for bdc
        bdc = copy(original)
        bdc(class_=self.__prop["burndownchart"]["class"],
            id=self.__prop["burndownchart"]["id"] % id, src=src)

        return bdc

    ############################################################################
    # IRequestHandler methods #
    #  - Extension point interface for request handlers
    #    (to insert custom templates)
    ############################################################################
    def match_request(self, req):
        """ Filters only requests matching these patterns to be processed. """

        return (req.path_info == '/inject/inject.js') \
                or (re.match(r'/jquery.*\.js$', req.path_info))

    def process_request(self, req):
        """ Return populated templates for these requests listened for. """

        if (req.path_info == '/inject/inject.js'):
            data = {
              "zoompanel" : self.__prop["zoompanel"]     ["class"]
            , "chart"     : self.__prop["burndownchart"] ["class"]
            , "container" : self.__prop["container"]     ["class"]
            }
            return 'inject.html', { 'data': data }, 'text/javascript'
        elif (re.match(r'/jquery.*\.js$', req.path_info)):
            cdn_js = URL_CDN_JQUERY
            opener = urllib2.build_opener()
            try:
                infile = opener.open(cdn_js)
            except URLError, msg:
                self.log.error("Unable to fetch jQuery JS from CDN: %s", msg)
                raise
            content = infile.read()
            return 'js.html', { 'data': { 'js' : content }}, 'text/javascript'

    ############################################################################
    # IRequestFilter methods #
    #  - Extension point interface for components that want to filter HTTP
    #    requests, before and/or after they are processed by the main handler
    ############################################################################
    def pre_process_request(self, req, handler):
        """ Preprocess incoming request & handler. (if any) """

        return handler

    def post_process_request(self, req, template, data, content_type):
        """ To requests for /{roadmap,milestone}, apply relevant CSS/JS. """

        if req.path_info[1:].startswith(('roadmap', 'milestone')):
            for css in ['burndownchart', 'jquery-ui-1.7.1.custom']:
                add_stylesheet(req, 'inject/css/%s.css' % css)

            this_htdocs, _ = self.get_htdocs_dirs()[0]
            baseurl = \
                os.path.join(req.chrome['htdocs_location'],'../',this_htdocs)
            add_script_data(req, { 'baseurl': baseurl })
            add_script(req, 'inject/js/preload.js')

            # check for existing jQuery library
            add_script(req, 'inject/js/jquery.js')

            add_script(req, 'inject/js/jquery-ui.js')
            add_script(req, '/inject/inject.js')

        return template, data, content_type

    ############################################################################
    # ITemplateProvider methods #
    #  - Used to add the plugin's templates and htdocs
    ############################################################################
    def get_htdocs_dirs(self):
        """Return a list of directories with static resources (such as style
        sheets, images, etc.)

        Each item in the list must be a `(prefix, abspath)` tuple. The
        `prefix` part defines the path in the URL that requests to these
        resources are prefixed with.

        The `abspath` is the absolute path to the directory containing the
        resources on the local file system.
        """
        return [('inject', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return a list of directories containing the provided template
        files.
        """
        return [resource_filename(__name__, 'templates')]
