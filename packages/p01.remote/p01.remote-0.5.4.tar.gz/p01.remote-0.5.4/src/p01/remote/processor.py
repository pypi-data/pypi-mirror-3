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
import logging
import persistent
import threading
import time

from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

import zope.interface
import zope.copy
import zope.location
from zope.traversing.api import getParents
from zope.container import contained

import zc.queue

from p01.remote import interfaces
from p01.remote import exceptions
from p01.remote import job
from p01.remote import worker
from p01.remote import scheduler


log = logging.getLogger('p01.remote')

storage = threading.local()


class RemoteProcessor(contained.Contained, persistent.Persistent):
    """A persistent remote processor.

    The remote queue uses local IJob component for processing. Such job
    objects get cloned if we need to process one.

    Some internals:

    _jobs -- stores the original job objects. This jobs are the master which
      get cloned if we need to process one.

    _processor -- stores all processing jobs. This allows us to get a job by id.

    _queue -- stores queued jobs before they get processed by a worker. This
      jobs get processed by a worker process. The jobs in this queue will get
      added if we create a new job.

    _scheduler -- stores scheduled items which know when a job should get
      processed. Jobs created by a scheduler will get processed without to
      store them in the _processor or _queue storages.


    Note: Scheduled jobs get not stored in the _queue, they get directly used
    from the scheduler.

    """
    zope.interface.implements(interfaces.IRemoteProcessor)

    workerFactory = worker.SimpleWorker
    workerArguments = {'waitTime': 1.0}

    def __init__(self):
        super(RemoteProcessor, self).__init__()
        self._counter = 1
        self._jobs = OOBTree()
        self._processor = IOBTree()
        self._queue = zc.queue.PersistentQueue()
        self._scheduler = scheduler.Scheduler()
        # locate them
        zope.location.locate(self._scheduler, self, u'++scheduler++')

    def addScheduler(self, item):
        """Add a new scheduler item."""
        self._scheduler.add(item)
        zope.location.locate(item, self, item.__name__)

    def addJob(self, name, job):
        """Add a new job as available job."""
        self._jobs[name] = job
        zope.location.locate(job, self, name)

    def getJobByName(self, name):
        return self._jobs.get(name, None)

    def _createJob(self, name, input=None):
        """See interfaces.IRemoteProcessor"""
        orgJob = self.getJobByName(name)
        if orgJob is None:
            raise ValueError("Job with given name '%s' does not exist" % name)

        jobId = self._counter
        self._counter += 1

        # clone job
        job = zope.copy.copy(orgJob)
        job.id = jobId
        job.input = input
        job.created = datetime.datetime.now()
        self._processor[jobId] = job
# TODO: should we not locate them within the jobId as name?
        # locate them with the same name as we had before
        zope.location.locate(job, self, name)
        return job

    def processJob(self, name, input=None):
        """See interfaces.IRemoteProcessor"""
        job = self._createJob(name, input)
        self._queue.put(job)
        job.queued = datetime.datetime.now()
        job.status = interfaces.QUEUED
        return job.id

    def removeJobs(self, stati=None):
        """See interfaces.IRemoteProcessor"""
        allowed = [interfaces.CANCELLED, interfaces.ERROR, interfaces.COMPLETED]
        if stati is None:
            stati = allowed
        if not isinstance(stati, list):
            stati = [stati]
        for key in list(self._processor.keys()):
            job = self._processor[key]
            if job.status in stati:
                if job.status not in allowed:
                    raise ValueError('Not allowed status for removing. %s' % \
                        job.status)
                del self._processor[key]
                job.__parent__ = None

    def cancelJob(self, jobid):
        """See interfaces.IRemoteProcessor"""
        # remove already queued job
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break
        # set status to cancelled
        if jobid in self._processor:
            job = self._processor[jobid]
            job.status = interfaces.CANCELLED

    def getJobStatus(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return self._processor[jobid].status

    def getJobResult(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return self._processor[jobid].output

    def getJobError(self, jobid):
        """See interfaces.IRemoteProcessor"""
        return str(self._processor[jobid].error)

    def reScheduleItem(self, item, callTime=None):
        if callTime is None:
            callTime = int(time.time())
        self._scheduler.reScheduleItem(item, callTime)

    def reScheduleItems(self, callTime=None):
        if callTime is None:
            callTime = int(time.time())
        self._scheduler.reScheduleItems(callTime)

    def pullNextJob(self, now=None):
        # return the next job
        if now is None:
            now = int(time.time())
        # get a scheduled job, note scheduled jobs do not get added to _queue
        item = self._scheduler.pullNextSchedulerItem(now)
        if item is not None:
            # create a job and store them in _processor and return them. Do not
            # store them in _queue. Not sure if this could run into conflicts
            # since we will add the job to the _jobs container.
            return self._createJob(item.jobName, item.input)
        # or get a job from the input queue
        if self._queue:
            return self._queue.pull()
        # there is no job available
        return None

    def processNextJob(self, now=None):
        """This method get called by a worker."""
        job = self.pullNextJob(now)
        if job is None:
            return False
        return self._processJob(job)

# not implemented right now, this whould be used if we implement multi thread
# aware workers
#    def processJobById(self, jobid):
#        """Process job by given Id."""
#        job = self._processor[jobid]
#        return self._processJob(job)

    def processJobs(self, now=None):
        """See interfaces.IRemoteProcessor"""
        # TODO: do we need to lock the worker thread?
        while self.processNextJob(now):
            pass

    def startProcessing(self):
        """See interfaces.IRemoteProcessor"""
        if self.isProcessing:
            log.info("RemoteProcessor '%s' already running" % self.__name__)
            return
        # Create the path to the remote queue within the DB.
        queuePath = [parent.__name__ for parent in getParents(self)
                     if parent.__name__]
        queuePath.reverse()
        # if we setup the remote queue as application root we do not have any
        # parent and __name__. But that's fine if we use an empty paths list
        if self.__name__:
            queuePath.append(self.__name__)
        # Start the thread running the processor inside.
        processor = self.workerFactory(
            self._p_jar.db(), queuePath, **self.workerArguments)
        thread = threading.Thread(target=processor, name=self._threadName)
        thread.setDaemon(True)
        thread.running = True
        thread.start()
        if self.__name__ is not None:
            name = self.__name__
        else:
            name = 'root'
        log.info("RemoteProcessor '%s' started" % name)

    def stopProcessing(self):
        """See interfaces.IRemoteProcessor"""
        name = self._threadName
        for thread in threading.enumerate():
            if thread.getName() == name:
                thread.running = False
                break

    @property
    def isProcessing(self):
        """See interfaces.IRemoteProcessor"""
        threadName = self._threadName
        for thread in threading.enumerate():
            if thread.getName() == threadName:
                if thread.running:
                    return True
                break
        return False

    # internal helpers
    def _processJob(self, job):
        """Knows how to process a given job."""
        job.started = datetime.datetime.now()
        if not hasattr(storage, 'runCounter'):
            storage.runCounter = 0
        storage.runCounter += 1
        try:
            job.output = job(self)
            job.status = interfaces.COMPLETED
        except exceptions.JobError, error:
            job.error = error
            job.status = interfaces.ERROR
        except Exception, error:
            if storage.runCounter <= 3:
                # TODO: move this to else and log the raising exception here
                log.error('Caught a generic exception, preventing thread '
                          'from crashing')
                log.exception(error)
                raise
            else:
                job.error = error
                job.status = interfaces.ERROR
        job.completed = datetime.datetime.now()
        job.runCounter = storage.runCounter
        storage.runCounter = 0
        return True

    @property
    def _threadName(self):
        """Return name of the processing thread."""
        # This name isn't unique based on the path to self, but this doesn't
        # change the name that's been used in past versions.
        try:
            path = [parent.__name__ for parent in getParents(self)
                    if parent.__name__]
        except TypeError:
            # not locatable
            path = []
        path.reverse()
        path.append('p01.remote')
        if self.__name__:
            path.append(self.__name__)
        else:
            path.append('as.root')
        return '.'.join(path)
