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

import datetime
import persistent

import zope.interface
from zope.container import contained
from zope.schema.fieldproperty import FieldProperty
from ZODB.interfaces import IDatabase
from ZODB.FileStorage.FileStorage import FileStorageError

from p01.remote import interfaces
from p01.remote import exceptions


class Job(contained.Contained, persistent.Persistent):
    """Job base class."""

    zope.interface.implements(interfaces.IJob)

    id = FieldProperty(interfaces.IJob['id'])
    status = FieldProperty(interfaces.IJob['status'])
    runCounter = FieldProperty(interfaces.IJob['runCounter'])
    input = FieldProperty(interfaces.IJob['input'])
    output = FieldProperty(interfaces.IJob['output'])
    error = FieldProperty(interfaces.IJob['error'])
    created = FieldProperty(interfaces.IJob['created'])
    queued = FieldProperty(interfaces.IJob['queued'])
    started = FieldProperty(interfaces.IJob['started'])
    completed = FieldProperty(interfaces.IJob['completed'])

    def __init__(self):
        super(Job, self).__init__()
        self.created = datetime.datetime.now()

    def __call__(self, remoteProcessor):
        """Process a job."""
        if self.started is None:
            raise exceptions.JobError("Processing a not started job.")

    def __repr__(self):
        if self.id is not None:
            id = ' %s' % self.id
        else:
            id = ''
        return '<%s %r%s>' %(self.__class__.__name__, self.__name__, id)


class RemoveCompletedJobsJob(Job):
    def __call__(self, remoteProcessor):
        super(RemoveCompletedJobsJob, self).__call__(remoteProcessor)

        remoteProcessor.removeJobs(interfaces.COMPLETED)


class PackZODBJob(Job):
    def __call__(self, remoteProcessor):
        super(PackZODBJob, self).__call__(remoteProcessor)

        status = []
        days = 0
        for name, db in zope.component.getUtilitiesFor(IDatabase):
            try:
                db.pack(days=days)
                msg = 'Database registered as "%s" successfully packed.' % name
            except FileStorageError, err:
                msg = 'ERROR packing database %s: %s' % (name, err)
            status.append(msg)

        status = '\n'.join(status)
