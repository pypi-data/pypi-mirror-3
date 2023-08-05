##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import unittest
from doctest import DocFileSuite

from van.testing.layer import zcml_layer

class ZCMLLayer:
    zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
zcml_layer(ZCMLLayer)

have_zpt = True
try:
    import zope.app.pagetemplate
except ImportError:
    have_zpt = False

def test_suite():
    suite = unittest.TestSuite()
    test = DocFileSuite('README.txt')
    test.layer = ZCMLLayer
    suite.addTest(test)
    if have_zpt:
        zpt_test = DocFileSuite('zpt.txt')
        zpt_test.layer = ZCMLLayer
        suite.addTest(zpt_test)
    return suite


