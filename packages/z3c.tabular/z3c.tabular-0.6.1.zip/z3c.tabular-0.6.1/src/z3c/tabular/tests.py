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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
import doctest
from zope.publisher.browser import TestRequest

import z3c.testing
import z3c.table.testing
from z3c.tabular import interfaces
from z3c.tabular import table
from z3c.tabular import testing


class FakeContainer(object):
    def values(self):
        pass


# table
class TestFormTable(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        z3c.table.testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.IFormTable

    def getTestClass(self):
        return table.FormTable

    def getTestPos(self):
        return (FakeContainer(), TestRequest())



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestFormTable),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
