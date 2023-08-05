#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-24


import unittest

from test_request import RequestDispatcherTest
from test_resource import ResourceBuilderTest, ResourceTest
from test_response import ResponseTest
from test_message import EntityTest
from test_debug import DebugTest
from test_context import ContextTest, ContextDataTest
from test_application import ApplicationTest, ResourceManagerTest


def suite():
    context = globals()
    suite = unittest.TestSuite()
    for test in context:
        if test.endswith('Test'):
            suite.addTest(unittest.makeSuite(context[test]))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
