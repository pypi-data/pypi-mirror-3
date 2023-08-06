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

import logging
import time

from zope.schema import ValidationError

from p01.remote import job
from p01.remote import exceptions
from p01.remote import processor


###############################################################################
#
# Testing stubs
#
###############################################################################

class EchoJob(job.Job):
    """A simple echo, job implementation."""

    def __call__(self, remoteProcessor):
        return self.input


class SleepJob(job.Job):
    """Sleep job."""

    def __call__(self, remoteProcessor):
        (sleepTime, id) = self.input
        time.sleep(sleepTime)
        log = logging.getLogger('p01.remote')
        log.info('Job: %i' %id)


class ErrorJob(job.Job):
    """A simple error job for testing."""

    def __call__(self, remoteProcessor):
        raise exceptions.JobError('An error occurred.')


class FatalJob(job.Job):
    """A fatal error for testing"""

    def __call__(self, remoteProcessor):
        raise ValidationError('An error occurred.')


###############################################################################
#
# testing setup
#
###############################################################################
from zope.testing.loggingsupport import InstalledHandler
from zope.app.testing.setup import placefulSetUp
from zope.app.testing.setup import placefulTearDown


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root

    log_info = InstalledHandler('p01.remote')
    test.globs['log_info'] = log_info
    test.origArgs = processor.RemoteProcessor.workerArguments
    processor.RemoteProcessor.workerArguments = {'waitTime': 0.0}


def tearDown(test):
    placefulTearDown()
    log_info = test.globs['log_info']
    log_info.clear()
    log_info.uninstall()
    processor.RemoteProcessor.workerArguments = test.origArgs
