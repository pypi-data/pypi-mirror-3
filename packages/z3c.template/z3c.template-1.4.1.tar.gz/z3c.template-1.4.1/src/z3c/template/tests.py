##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id: tests.py 124401 2012-02-15 17:50:33Z menesis $
"""
__docformat__ = "reStructuredText"

from zope.app.testing import setup
from zope.configuration import xmlconfig
import doctest
import itertools
import unittest

import z3c.template.template


def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root

def tearDown(test):
    setup.placefulTearDown()

def setUpZPT(suite):
    setUp(suite)

def setUpZ3CPT(suite):
    setUp(suite)
    import z3c.pt
    import z3c.ptcompat
    xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    xmlconfig.XMLConfig('configure.zcml', z3c.ptcompat)()

    # We have to cook this template explicitly, because it's a module
    # global.
    from z3c.template.template import Macro
    Macro.wrapper._cook()


def test_suite():
    tests = ((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('zcml.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ) for setUp in (setUpZPT, setUpZ3CPT,))

    return unittest.TestSuite(itertools.chain(*tests))
