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

import z3c.table.interfaces


class ITemplateTable(z3c.table.interfaces.ITable):
    """Template aware table."""


class IFormTable(ITemplateTable):
    """Table including a form setup."""


class IDeleteFormTable(IFormTable):
    """Delete button aware table including a form setup."""


class ISubFormTable(IDeleteFormTable):
    """Table including a sub form for one selected item."""
