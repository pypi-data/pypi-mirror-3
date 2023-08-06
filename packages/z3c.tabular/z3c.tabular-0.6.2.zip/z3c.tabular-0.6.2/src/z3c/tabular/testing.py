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

from zope.browserpage import metaconfigure
from zope.app.testing import setup

import z3c.macro.tales
import z3c.table.testing


###############################################################################
#
# testing setup
#
###############################################################################

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

    metaconfigure.registerType('macro', z3c.macro.tales.MacroExpression)
    z3c.table.testing.setUpAdapters()


def tearDown(test):
    setup.placefulTearDown()
