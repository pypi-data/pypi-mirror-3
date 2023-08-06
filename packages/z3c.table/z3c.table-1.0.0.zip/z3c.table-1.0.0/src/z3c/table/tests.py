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
from z3c.batching.batch import Batch
from z3c.table import testing
from z3c.table import interfaces
from z3c.table import table
from z3c.table import column
from z3c.table import batch


class FakeContainer(object):

    def values(self):
        pass


# table
class TestTable(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.Table

    def getTestPos(self):
        return (FakeContainer(), TestRequest())


class TestSequenceTable(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.SequenceTable

    def getTestPos(self):
        return (None, TestRequest())


# column
class TestColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.Column

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNoneCell(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.INoneCell

    def getTestClass(self):
        return column.NoneCell

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNameColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.NameColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestRadioColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.RadioColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestCheckBoxColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.CheckBoxColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


# batch
class TestBatchProvider(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IBatchProvider

    def getTestClass(self):
        return batch.BatchProvider

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        t.rows = Batch([])
        return ({}, TestRequest(), t)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('sequence.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('sort.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('batch.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_UDIFF,
            ),
        doctest.DocFileSuite('miscellaneous.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('column.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestTable),
        unittest.makeSuite(TestSequenceTable),
        unittest.makeSuite(TestColumn),
        unittest.makeSuite(TestNoneCell),
        unittest.makeSuite(TestNameColumn),
        unittest.makeSuite(TestRadioColumn),
        unittest.makeSuite(TestCheckBoxColumn),
        unittest.makeSuite(TestBatchProvider),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
