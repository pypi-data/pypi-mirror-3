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

import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.table import interfaces


class ValuesMixin(object):
    """Mixin for different value adapters."""

    zope.interface.implements(interfaces.IValues)

    def __init__(self, context, request, table):
        self.context = context
        self.request = request
        self.table = table


class ValuesForContainer(ValuesMixin):
    """Values from a simple IContainer."""

    zope.component.adapts(zope.interface.Interface, IBrowserRequest,
        interfaces.ITable)

    @property
    def values(self):
        return self.context.values()


class ValuesForSequence(ValuesMixin):
    """Values from a simple IContainer."""

    zope.component.adapts(zope.interface.Interface, IBrowserRequest,
        interfaces.ISequenceTable)


    @property
    def values(self):
        return self.context