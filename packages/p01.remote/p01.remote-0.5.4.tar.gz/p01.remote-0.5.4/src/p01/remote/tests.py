##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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

from z3c.testing import InterfaceBaseTest

from p01.remote import interfaces
from p01.remote import processor
from p01.remote import scheduler
from p01.remote import worker
from p01.remote import testing


class RemoteProcessorTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IRemoteProcessor

    def getTestClass(self):
        return processor.RemoteProcessor


class SimpleWorkerTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IWorker

    def getTestClass(self):
        return worker.SimpleWorker

    def getTestPos(self):
        return (None, None)


class SchedulerTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IScheduler

    def getTestClass(self):
        return scheduler.Scheduler


class CronTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ICron

    def getTestClass(self):
        return scheduler.Cron

    def getTestPos(self):
        return (u'jobName',)


class DelayTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IDelay

    def getTestClass(self):
        return scheduler.Delay

    def getTestPos(self):
        return (u'jobName',)


class EchoJobTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.EchoJob


class ErrorJobTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.ErrorJob


class SleepJobTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IJob

    def getTestClass(self):
        return testing.SleepJob


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=testing.setUp,
                     tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     |doctest.ELLIPSIS
                     ),
        doctest.DocFileSuite('scheduler.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        doctest.DocFileSuite('worker.txt',
                     setUp=testing.setUp,
                     tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     |doctest.ELLIPSIS
                     ),
        unittest.makeSuite(RemoteProcessorTest),
        unittest.makeSuite(SimpleWorkerTest),
        unittest.makeSuite(SchedulerTest),
        unittest.makeSuite(CronTest),
        unittest.makeSuite(DelayTest),
        unittest.makeSuite(EchoJobTest),
        unittest.makeSuite(ErrorJobTest),
        unittest.makeSuite(SleepJobTest),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
