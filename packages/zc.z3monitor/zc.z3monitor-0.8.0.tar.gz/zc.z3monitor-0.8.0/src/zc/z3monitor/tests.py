##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import renormalizing, setupstack
import doctest
import logging
import mock
import re
import sys
import unittest
import ZODB.MappingStorage


class FauxCache:

    @property
    def fc(self):
        return self

    def getStats(self):
        return 42, 4200, 23, 2300, 1000

def is_connected(self):
    return self._is_connected

ZODB.MappingStorage.MappingStorage._cache = FauxCache()
ZODB.MappingStorage.MappingStorage._is_connected = True
ZODB.MappingStorage.MappingStorage.is_connected = is_connected

def setUpInitialize(test):
    for name in (
        'zope.app.appsetup.product.getProductConfiguration',
        'zope.component.getUtilitiesFor',
        'ZODB.ActivityMonitor.ActivityMonitor',
        'zc.monitor.start',
        ):
        setupstack.context_manager(test, mock.patch(name))

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            checker=renormalizing.RENormalizing([
                (re.compile("Vm(Size|RSS):\s+\d+\s+kB"), 'Vm\\1 NNN kB'),
                (re.compile("\d+[.]\d+ seconds"), 'N.NNNNNN seconds'),
                ]),
            ),
        doctest.DocFileSuite(
            'initialize.test',
            setUp = setUpInitialize, tearDown=setupstack.tearDown,
            )
        ))
