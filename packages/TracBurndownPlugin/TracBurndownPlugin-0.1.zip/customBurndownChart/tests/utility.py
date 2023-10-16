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

import shutil
import tempfile
from test_harness        import TestHarness
from StringIO            import StringIO
from trac.perm           import PermissionCache, PermissionSystem
from trac.test           import EnvironmentStub, Mock
from trac.web.api        import Request
from trac.web.href       import Href
from trac.ticket.model   import Milestone
from customBurndownChart.config import init_config
try:
    from trac.perm import DefaultPermissionPolicy
except ImportError:
    DefaultPermissionPolicy = None

ESTIMATION_FIELD = 'estimatedtime'

def getNotContainsInList(needles, haystack):
    """
        Helper function to filter list from needles
        for items which are not substrings of any
        items in haystack.
    """

    matches = []
    for needle in needles:
        for item in haystack:
            if needle in item:
                matches.append(needle)

    return [ item for item in needles if item not in matches ]

def make_environ(scheme='http', server_name='localhost', server_port=8000,
    method='GET', script_name='/trac', **kwargs):
    """ Utility to setup environment variable. """

    environ = {
        'wsgi.url_scheme': scheme, 'wsgi.input': StringIO(''),
        'REQUEST_METHOD': method, 'SERVER_NAME': server_name,
        'SERVER_PORT': server_port, 'SCRIPT_NAME': script_name
    }
    environ.update(kwargs)
    return environ

def do_init_setup_class(cls):
    """ Utility to setup class unittest. """

    print "\n\tBeginning unittests, setting up %s...\n" % cls
    cls.env = EnvironmentStub(default_data=True,
        enable=['trac.*', 'perm.*', 'estimationtools.*'])

    # create temp directory
    cls.env.path = tempfile.mkdtemp()

    cls.test_harness = TestHarness(cls.env, ESTIMATION_FIELD)

    # set default config options
    cls.config = init_config(cls.env, ESTIMATION_FIELD)

    # set up permissions
    if DefaultPermissionPolicy is not None \
        and hasattr(DefaultPermissionPolicy, "CACHE_EXPIRY"):
        cls.old_perm_cache_expiry = DefaultPermissionPolicy.CACHE_EXPIRY
        DefaultPermissionPolicy.CACHE_EXPIRY = -1

    # setup mock repository
    cls.repos = Mock(
        get_node=lambda path, rev=None:
            Mock(get_history=lambda: [], isdir=True),
        normalize_path=lambda path: path,
        sync=lambda: None
    )
    cls.env.get_repository = lambda authname=None: cls.repos

    if not cls.env.is_component_enabled('EstimationTools'):
        raise RuntimeError("EstimationTools plugin is not enabled.")

def do_init_teardown_class(cls):
    """ Utility to teardown class unittest. """

    print "\n\tAll tests() executed, unittest complete...tearing down %s..." \
        % cls

    # reset permission policy
    if DefaultPermissionPolicy is not None and hasattr(DefaultPermissionPolicy, "CACHE_EXPIRY"):
        DefaultPermissionPolicy.CACHE_EXPIRY = cls.old_perm_cache_expiry

    # delete temp directory
    shutil.rmtree(cls.env.path)

    conn = cls.env.get_db_cnx()
    cursor = conn.cursor()
    cursor.close()
    conn.close()
    cursor = conn = None
    del [ cursor, conn ]

def do_init_setup(self):
    """ Utility to setup method unittest. """

    # set up new HTTP web request
    self.req = Request(make_environ(), lambda a,b:True)
    self.req.href = Href('/')
    self.req.abs_href = Href('http://localhost:8000/')
    self.req.tz = 'UTC'
    self.req.authname = 'lshift'
    self.req.perm = PermissionCache(self.env, 'lshift')
    self.req.chrome = { 'warnings': [] }

    self.formatter = Mock(req=self.req)

    # ensure no tickets initially
    self.assertEqual(0, self.test_harness._num_tix())

    # pretty print all ticket info
    #self.test_harness._all_tix()

    # track all milestones initially
    self.milestones = set(self.test_harness.milestone_get())

    self.env.config.set('trac', 'permission_store', 'DefaultPermissionStore')
    PermissionSystem(self.env).revoke_permission('lshift', 'TRAC_ADMIN')

def do_init_teardown(self):
    """ Utility to teardown method unittest. """

    # reset tickets
    self.test_harness.tix_delete_all()
    self.assertEqual(0, self.test_harness._num_tix())

    # reset milestones
    new_milestones = self.test_harness.milestone_get()\
                        .difference(self.milestones)
    [ Milestone(self.env, name).delete() for (_, name) in new_milestones ]

    # rest work hours
    self.env.config.set('estimation-tools', 'daily_work_hours', 8)

    self.env.reset_db()
