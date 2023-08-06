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

import zope.interface
import zope.schema
import zope.i18nmessageid
import zope.publisher.interfaces
from zope.location.interfaces import IPossibleSite

_ = zope.i18nmessageid.MessageFactory('p01')

QUEUED = 'queued'
CANCELLED = 'cancelled'
COMPLETED = 'completed'
ERROR = 'error'

JOB_STATUS_NAMES = [
    QUEUED,
    CANCELLED,
    COMPLETED,
    ERROR,
]


class IRemoteProcessor(zope.interface.Interface):
    """A compoent for managing and executing long-running, remote process."""

    isProcessing = zope.schema.Bool(
            title=_(u'Is processing'),
            description=_(u'Check whether the jobs are being processed'),
            default=False,
            )

    def addScheduler(item):
        """Add scheduler item."""

    def addJob(name, job):
        """Add a new job by the given job name.

        * name argument is a string specifying the (named) job.
        * input are arguments for job processing.
          to be started later with calling processJob
        """

    def getJobByName(name):
        """Return a job by name."""

    def processJob(name, input=None):
        """Process an available job by the given job name.

        * name argument is a string specifying the job by it's name.
        * input are arguments for job processing.
        """

    def removeJobs(stati=None):
        """Remove all jobs which are completed or canceled or have errors by
        the given stati.
        
        If no stati is given all stati are used for abort jobs. Note: abortJobs
        will remove jobs from the processor but not remove the original job
        object.
        """

    def cancelJob(jobid):
        """Cancel a particular job."""

    def getJobStatus(jobid):
        """Get the status of a job."""

    def getJobResult(jobid):
        """Get the result data structure of the job."""

    def getJobError(jobid):
        """Get the error of the job."""

    def reScheduleItem(item, callTime=None):
        """Re-schedule item."""

    def reScheduleItems(callTime=None):
        """Re-schedule items."""

    def pullNextJob(now=None):
        """Pull next job."""

    def processNextJob(now=None):
        """Process the next job in the queue.

        This method get called from a worker thread.
        """

    def processJobs(now=None):
        """Process all scheduled jobs.

        This call blocks the thread it is running in.
        """

    def startProcessing():
        """Start processing jobs.

        This method has to be called after every server restart.
        """

    def stopProcessing():
        """Stop processing jobs."""


class IRemoteProcessorSite(IPossibleSite, IRemoteProcessor):
    """Remote processor IPossibleSite."""


class IJob(zope.interface.Interface):
    """An internal job object."""

    __name__ = zope.schema.TextLine(
        title=u'Job Name',
        description=u'The available job name.',
        required=True)

    id = zope.schema.Int(
        title=u'Id',
        description=u'The job id.',
        required=True)

    status = zope.schema.Choice(
        title=u'Status',
        description=u'The current status of the job.',
        values=JOB_STATUS_NAMES,
        required=True)

    runCounter = zope.schema.Int(
        title=u'Run counter',
        description=u'Run counter',
        default=0,
        required=True)

    input = zope.schema.Object(
        title=u'Input',
        description=u'The input for processing a job.',
        schema=zope.interface.Interface,
        required=False)

    output = zope.schema.Object(
        title=u'Output',
        description=u'The output of a processed job.',
        schema=zope.interface.Interface,
        required=False,
        default=None)

    error = zope.schema.Object(
        title=u'Error',
        description=u'The error object when the job processing failed.',
        schema=zope.interface.Interface,
        required=False,
        default=None)

    created = zope.schema.Datetime(
        title=u'Creation Date',
        description=u'The date/time at which the job was created.',
        required=True)

    queued = zope.schema.Datetime(
        title=u'Queued Date',
        description=u'The date/time at which the job was queued for processsing.',
        required=True)

    started = zope.schema.Datetime(
        title=u'Start Date',
        description=u'The date/time at which the job was started.')

    completed = zope.schema.Datetime(
        title=u'Completion Date',
        description=u'The date/time at which the job was completed.')

    def __call__(remoteProcessor):
        """Process a job."""


class IScheduler(zope.interface.Interface):
    """Scheduler manages scheduler items."""

    def add(item):
        """Add scheduler item."""

    def remove(item):
        """Remove scheduler item."""

    def get(key):
        """Return the item by the given key or None."""

    def __contains__(key):
        """Returns True or False if item with given key exists."""

    def keys():
        """Return scheduler item keys."""

    def values():
        """Return scheduler items."""

    def reScheduleItem(item, callTime=None):
        """Re-schedule item."""

    def reScheduleItems(callTime=None):
        """Re-schedule items."""

    def pullNextSchedulerItem(now=None):
        """Get next pending scheduler item based on now and the scheduled time.
        """

class ISchedulerItem(zope.interface.Interface):
    """Cron based scheduler item."""

    jobName = zope.schema.TextLine(
        title=_(u'Job name'),
        description=_(u'The scheduled job name'),
        required=True
        )

    input = zope.schema.Object(
        title=u'Input',
        description=u'The input for processing a job.',
        schema=zope.interface.Interface,
        required=False)

    active = zope.schema.Bool(
        title=_(u'Active'),
        description=_(u'Marker for active scheduler items.'),
        default=True,
        required=True
        )

    nextCallTime = zope.schema.Int(
        title=_(u'Next call time'),
        description=_(u'Next call time'),
        default=0,
        required=True
        )

    def getNextCallTime(now):
        """Returns the next call time if smaller then the given callTime.
        
        This method is also responsible for update the nextCallTime which get
        used for compare the next call time if this method returns a timestamp.
        """


class IDelay(ISchedulerItem):
    """Delay based scheduler item."""

    delay = zope.schema.Int(
        title=_(u'delay (second)'),
        description=_(u'delay (second)'),
        default=0,
        required=False
        )


class ICron(ISchedulerItem):
    """Scheduler parameter for IJob."""

    minute = zope.schema.Tuple(
        title=_(u'Minute(s) (0 - 59)'),
        description=_(u'Minute(s)'),
        value_type=zope.schema.Int(
            title=_(u'Minute'),
            description=_(u'Minute'),
            min=0,
            max=59,
            ),
        default=(),
        required=False
        )

    hour = zope.schema.Tuple(
        title=_(u'Hour(s) (0 - 23)'),
        description=_(u'Hour(s)'),
        value_type=zope.schema.Int(
            title=_(u'Hour'),
            description=_(u'Hour'),
            min=0,
            max=23,
            ),
        default=(),
        required=False
        )

    dayOfMonth = zope.schema.Tuple(
        title=_(u'Day of month (1 - 31)'),
        description=_(u'Day of month'),
        value_type=zope.schema.Int(
            title=_(u'Day of month'),
            description=_(u'Day of month'),
            min=1,
            max=31,
            ),
        default=(),
        required=False
        )

    month = zope.schema.Tuple(
        title=_(u'Month(s) (1 - 12)'),
        description=_(u'Month(s)'),
        value_type=zope.schema.Int(
            title=_(u'Month'),
            description=_(u'Month'),
            min=1,
            max=12,
            ),
        default=(),
        required=False
        )

    dayOfWeek = zope.schema.Tuple(
        title=_(u'Day of week (0 - 6)'),
        description=_(u'Day of week'),
        value_type=zope.schema.Int(
            title=_(u'Day of week'),
            description=_(u'Day of week'),
            min=0,
            max=6,
            ),
        default=(),
        required=False
        )


class IJobNameTermsAware(zope.interface.Interface):
    """Force to use a select field for our jobName selection."""


class IWorkerPublication(zope.publisher.interfaces.IPublication):
    """Worker request providing annotation."""


class IWorkerRequest(zope.publisher.interfaces.IRequest):
    """Worker request providing annotation."""


class IWorker(zope.interface.Interface):
    """Job Worker

    Process the jobs that are waiting in the queue. A worker is meant to
    be run in a separate thread. To complete a job, it simply calls back into
    the remote queue. This works, since it does not use up any Web server
    threads.

    Processing a job can take a long time. However, we do not have to worry
    about transaction conflicts, since no other request is touching the job
    object. But be careful it's always possible that if the job manipulates
    something that this could force to run into a conflict error.

    """

    running = zope.schema.Bool(
        title=_(u"Running Flag"),
        description=_(u"Tells whether the worker is currently running."),
        readonly=True)

    def __init__(db, queuePath, waitTime=1.0):
        """Initialize the worker.

        The ``db`` is a ZODB instance that is used to call back into the remote
        queue. The ``queuePath`` specifies how to traverse to the remote
        queue itself.
        """

    def __call__():
        """Run the worker."""
