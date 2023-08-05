##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Schema-generation tests

$Id: tests.py 124134 2012-01-23 15:20:44Z menesis $
"""

from zope.app.testing import placelesssetup
import doctest
import unittest


def tearDownREADME(test):
    placelesssetup.tearDown(test)
    test.globs['db'].close()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=placelesssetup.setUp, tearDown=tearDownREADME,
            ),
        doctest.DocTestSuite('zope.app.generations.generations'),
        doctest.DocTestSuite('zope.app.generations.utility'),
        ))
