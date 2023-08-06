##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""

import doctest
import re
import unittest
import z3c.layer.pagelet.testing
import zope.testing.renormalizing


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])


def create_suite(*args, **kw):
    kw['optionflags'] = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    kw['globs'] = dict(
        getRootFolder=z3c.layer.pagelet.testing.TestLayer.getRootFolder)
    suite = doctest.DocFileSuite(*args, **kw)
    suite.layer = z3c.layer.pagelet.testing.TestLayer
    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(create_suite('../README.txt', checker=checker))
    suite.addTest(create_suite('bugfixes.txt'))
    return suite
