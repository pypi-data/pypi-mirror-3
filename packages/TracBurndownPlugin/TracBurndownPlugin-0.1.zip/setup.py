#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 LShift
# All rights reserved.
#

""" Burndown chart plugin for milestones in Trac. """

from setuptools import setup, find_packages

setup(
    name         = 'TracBurndownPlugin',
    version      = '0.1',
    description  = 'Burndown chart plugin for milestones in Trac',
    long_description = """
        LShift internal Trac plugin component to display
        Burndown charts for milestones using Google's Chart API.
    """,
    author       = 'Lee Wei',
    author_email = 'leewei@lshift.net',
    license      = 'BSD',
    url          = 'http://www.lshift.net/',
    download_url = 'http://www.lshift.net/',
    keywords     = 'trac burndown chart plugin',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Version Control',
    ],
    packages = find_packages(exclude=['*.tests*']),
    install_requires = [
        'setuptools>=0.6b1',
        'Trac>=0.12',
        'EstimationTools>=0.4.5'
    ],
    extras_require={
        'estimationtools': 'EstimationTools'
    },
    entry_points = {
        'trac.plugins': [
            'customBurndownChart = customBurndownChart'
        ]
    },
    include_package_data=True,
    package_data = {
        'customBurndownChart': [
            'htdocs/css/*.css', 'htdocs/img/*', 'htdocs/js/*.js',
            'templates/*.html'
        ]
    },
    test_suite = 'customBurndownChart.tests.test_suite',
    tests_require = [],
    zip_safe = False
)
