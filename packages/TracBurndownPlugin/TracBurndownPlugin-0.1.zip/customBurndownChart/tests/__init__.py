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

from unittest import TestSuite, makeSuite, TextTestRunner

def test_suite():
    suite = TestSuite()

    from api import TestHarnessTestCase
    suite.addTest(makeSuite(TestHarnessTestCase, 'test'))

    from embed import EmbedTestCase
    suite.addTest(makeSuite(EmbedTestCase, 'test'))
    from inject import InjectTestCase
    suite.addTest(makeSuite(InjectTestCase, 'test'))
    from prefs import PrefsTestCase
    suite.addTest(makeSuite(PrefsTestCase, 'test'))
    from tooltip import TooltipTestCase
    suite.addTest(makeSuite(TooltipTestCase, 'test'))

    return suite

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(test_suite())
