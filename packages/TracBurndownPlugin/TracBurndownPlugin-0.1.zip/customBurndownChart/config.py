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

URL_CDN_JQUERY = 'http://code.jquery.com/jquery-latest.min.js'
URL_CDN_QTIP2  = 'http://craigsworks.com/projects/qtip2/packages/latest'

SECTION_NAME   = 'estimation-tools'
DEFAULT_CHART_DISPLAY = { 'unit': 'hours' }

def init_config(env, estimation_field):
    config_options = {
        'trac': [
            ('permission_store', 'DefaultPermissionStore')
        ],
        'components': [
            ('estimationtools.*', 'enabled')
        ],
        'estimation-tools': [
            ('estimation_field', estimation_field)
        ],
        'ticket-custom': [
            ('estimatedtime', 'text'),
            ('estimatedtime.label', 'Remaining Time'),
            ('estimatedtime.value', 0)
        ]
    }
    config = env.config
    for section, kvs in config_options.iteritems():
        [ config.set(section, key, value) for key, value in kvs ]
    config.save()
