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
import threading
import time
import zope.interface
import zope.publisher.publish

from p01.remote import interfaces
from p01.remote import publisher

ERROR_MARKER = object()

log = logging.getLogger('p01.remote')


class SimpleWorker(object):
    """Single thread worker

    This worker only processes one job at a time.
    """
    zope.interface.implements(interfaces.IWorker)

    def __init__(self, db, queuePath, waitTime=1.0):
        self.db = db
        self.queuePath = queuePath
        self.waitTime = waitTime

    @property
    def running(self):
        th = threading.currentThread()
        if hasattr(th, 'running'):
            return th.running
        # fallback for InterfaceBaseTest
        return False

    def call(self, method, args=(), errorValue=ERROR_MARKER):
        # Create the path to the method.
        path = self.queuePath[:] + [method]
        path.reverse()
        request = publisher.WorkerRequest(*args)
        request.setPublication(publisher.WorkerPublication(self.db))
        request.setTraversalStack(path)
        # Publish the request, making sure that *all* exceptions are
        # handled. The processor should *never* crash.
        try:
            zope.publisher.publish.publish(request, False)
            return request.response._result
        except Exception, error:
            # This thread should never crash, thus a blank except
            log.error('Worker: ``%s()`` caused an error!' %method)
            log.exception(error)
            return errorValue is ERROR_MARKER and error or errorValue

    def processNextJob(self):
        return self.call('processNextJob', args=(None,))

    def __call__(self):
        while self.running:
            result = self.processNextJob()
            # If there are no jobs available, sleep a little bit and then
            # check again.
            if not result:
                time.sleep(self.waitTime)
