======
README
======

This package offers a remote processor. This remote processor could be used
as a mixin for utilities, sites or any other component. The processor can
execute pre defined jobs in another thread. It is also possible to run cron
jobs at specific times. Most parts of this implementation where taken from the
lovely.remotetask package which I helped to implement for lovely systems.

The main reason for a new implementation is the simpler and more generic
concept which this package provides. At the time we implemented the
lovely.remotetask package, the focus was to get a remote server which is able
to process predefined tasks. This implementation can be used as a mixin for
doing this but it also can be used for process components as jobs at the same
server with a delay or scheduled. e.g. delayed catalog indexing.


Usage
-----

  >>> import zope.component
  >>> import p01.remote.job
  >>> from p01.remote import testing
  >>> STOP_SLEEP_TIME = 0.02

Let's now start by create two a remote processor. We can use our remote queue
site implementation:

  >>> from zope.site import LocalSiteManager
  >>> from zope.security.proxy import removeSecurityProxy
  >>> from p01.remote import interfaces
  >>> import p01.remote.processor

  >>> firstQueue = p01.remote.processor.RemoteProcessor()

  >>> secondQueue = p01.remote.processor.RemoteProcessor()

The remote processor should be located, so it gets a name:

  >>> root['first'] = firstQueue
  >>> firstQueue.__parent__ is root
  True

  >>> root['second'] = secondQueue
  >>> secondQueue.__parent__ is root
  True

Let's discover the available jobs:

  >>> dict(firstQueue._jobs)
  {}

  >>> dict(secondQueue._jobs)
  {}

This list is initially empty, because we have not added any job. Let's
now define a job that simply echos an input string:

  >>> echoJob = testing.EchoJob()

Now we can set the job input:

  >>> echoJob.input = {'foo': 'blah'}

The only API requirement on the job is to be callable. Now we make sure that
the job works:

  >>> echoJob(firstQueue)
  {'foo': 'blah'}

Let's add the job to the available job list:

  >>> firstQueue.addJob(u'echo', echoJob)

The echo job is now available in the remote processor:

  >>> dict(firstQueue._jobs)
  {u'echo': <EchoJob u'echo'>}

  >>> dict(secondQueue._jobs)
  {}

Since the remote processor cannot instantaneously complete a job, incoming jobs
are managed by a queue. First we request the echo job to be executed:

  >>> jobid = firstQueue.processJob(u'echo', {'foo': 'bar'})
  >>> jobid
  1

The ``processJob()`` function schedules the job called "echo" to be executed
with the specified arguments. The method returns a job id with which we can
inquire about the job.
By default the ``processJob()`` function adds and starts the job ASAP.

  >>> firstQueue.getJobStatus(jobid)
  'queued'

Since the job has not been processed, the status is set to "queued". Further,
there is no result available yet:

  >>> firstQueue.getJobResult(jobid) is None
  True

As long as the job is not being processed, it can be cancelled:

  >>> firstQueue.cancelJob(jobid)
  >>> firstQueue.getJobStatus(jobid)
  'cancelled'

The firstQueue isn't being started by default:

  >>> firstQueue.isProcessing
  False

To get a clean logging environment let's clear the logging stack::

  >>> log_info.clear()

The recommended way to start a remote processor is a bootstrap susbcriber
registered for the IDatabaseOpenedEvent. This subscriber has to find the
remote processor instance in your DB and must call startProcessing. Let's open
a database connection and add our root to the db. The remote processor requires
that it's been committed to the database before it can be used:

  >>> from ZODB.tests import util
  >>> import transaction
  >>> db = util.DB()
  >>> from zope.app.publication.zopepublication import ZopePublication
  >>> conn = db.open()
  >>> conn.root()[ZopePublication.root_name] = root
  >>> transaction.commit()

Now we can start the remote processor by calling ``startProcessing``:

  >>> firstQueue.startProcessing()

and voila - the remote processor is processing:

  >>> firstQueue.isProcessing
  True

Checking out the logging will prove the started remote processor:

  >>> print log_info
  p01.remote INFO
    RemoteProcessor 'first' started

Let's now read a job:

  >>> jobid = firstQueue.processJob(u'echo', {'foo': 'bar'})
  >>> firstQueue.processJobs()

  >>> firstQueue.getJobStatus(jobid)
  'completed'
  >>> firstQueue.getJobResult(jobid)
  {'foo': 'bar'}

Now, let's define a new job that causes an error:

  >>> errorJob = testing.ErrorJob()
  >>> firstQueue.addJob(u'error', errorJob)

Now add and execute it:

  >>> jobid = firstQueue.processJob(u'error')
  >>> firstQueue.processJobs()

Let's now see what happened:

  >>> firstQueue.getJobStatus(jobid)
  'error'
  >>> firstQueue.getJobError(jobid)
  'An error occurred.'

Try at also with a not so nice error:

  >>> fatalJob = testing.FatalJob()
  >>> firstQueue.addJob(u'fatal', fatalJob)

Now add and execute it:

  >>> jobid = firstQueue.processJob(u'fatal')
  >>> firstQueue.processJobs()
  Traceback (most recent call last):
  ...
  ValidationError: An error occurred.

And force it:

  >>> jobid = firstQueue.processJob(u'fatal')
  >>> firstQueue.processJobs()
  Traceback (most recent call last):
  ...
  ValidationError: An error occurred.

And force it:

  >>> jobid = firstQueue.processJob(u'fatal')
  >>> firstQueue.processJobs()
  Traceback (most recent call last):
  ...
  ValidationError: An error occurred.

And force it. Fourth failure is a special case, now it does not re-raise
the exception but it gets set in job.error.

  >>> jobid = firstQueue.processJob(u'fatal')
  >>> firstQueue.processJobs()

Let's now see what happened:

  >>> firstQueue.getJobStatus(jobid)
  'error'
  >>> firstQueue.getJobError(jobid)
  'An error occurred.'


For management purposes, the remote processor also allows you to inspect all
jobs:

  >>> dict(firstQueue._processor)
  {1: <EchoJob u'echo' 1>, 2: <EchoJob u'echo' 2>, 3: <ErrorJob u'error' 3>,
  4: <FatalJob u'fatal' 4>, 5: <FatalJob u'fatal' 5>, 6: <FatalJob u'fatal' 6>,
  7: <FatalJob u'fatal' 7>}

To get rid of jobs not needed anymore we can use the reomveJobs method.

  >>> jobid = firstQueue.processJob(u'echo', {'blah': 'blah'})
  >>> sorted([job.status for job in firstQueue._processor.values()])
  ['cancelled', 'completed', 'error', 'error', 'queued', 'queued',
  'queued', 'queued']

  >>> firstQueue.removeJobs()

  >>> sorted([job.status for job in firstQueue._processor.values()])
  ['queued', 'queued', 'queued', 'queued']

Now process the last pending job and make sure we do not get more jobs:

  >>> firstQueue.pullNextJob()
  <EchoJob u'echo' 8>


Scheduling
----------

Scheduling jobs is done with an additional scheduler implementation. This
scheduler can contain scheduler items whihc provide scheduler information.
Let's  setup such a scheduler item and add them to the remote processors
scheduler container:

  >>> scheduledEcho = p01.remote.scheduler.Delay(u'echo', 10, startTime=0)
  >>> scheduledEcho.delay
  10
  >>> scheduledEcho.nextCallTime
  10

Before we add our scheduler item, make sure that we do not get a job from
the remote processor:

  >>> firstQueue.pullNextJob()
  >>> scheduledEcho.nextCallTime
  10

Now we can add our scheduler items to the remote processor scheduler:

  >>> firstQueue._scheduler.add(scheduledEcho)
  >>> sorted(firstQueue._scheduler.values())
  [<Delay 1 for: u'echo'>]
  >>> scheduledEcho.nextCallTime
  10

Now let's test if we will get the schdeuled job referenced by the scheduler
items jobName:

  >>> firstQueue.pullNextJob(0)

As you can see, we didn't get a job. This is because we used a call time smaller
then our scheduled item defines. But with a larger callTime then our scheduler
item calculated, we will get a new job:

  >>> firstQueue.pullNextJob(40)
  <EchoJob u'echo' 9>

  >>> firstQueue.pullNextJob(49)

  >>> firstQueue.pullNextJob(50)
  <EchoJob u'echo' 10>

if we execute the job at second 65, we will get the next scheduled time 10
seconds after that next call time:

  >>> firstQueue.pullNextJob(65)
  <EchoJob u'echo' 11>

  >>> firstQueue.pullNextJob(74)

  >>> firstQueue.pullNextJob(75)
  <EchoJob u'echo' 12>

For more information about scheduled job execution, see the scheduler.txt
documentation.


Threading behavior
------------------

Each remote processor runs in a separate thread, allowing them to operate
independently. Jobs should be designed to avoid conflict errors in
the database. If this is not possible, probably a transaction data manager
should be used which could revert changes on conflicts if external systems are
involved.

Let's start the remote processor we have defined at this point, and see what
threads are running as a result::


  >>> secondQueue.startProcessing()

  >>> import pprint
  >>> import threading

  >>> def show_threads():
  ...     threads = [t for t in threading.enumerate()
  ...                if t.getName().startswith('p01.remote.')]
  ...     threads.sort(key=lambda t: t.getName())
  ...     pprint.pprint(threads)

  >>> show_threads()
  [<Thread(p01.remote.first, started daemon ...)>,
   <Thread(p01.remote.second, started daemon ...)>]

Let's stop the remote processor, and give the background threads a chance to get
the message::

  >>> firstQueue.stopProcessing()
  >>> secondQueue.stopProcessing()

  >>> import time; time.sleep(STOP_SLEEP_TIME)

The threads have exited now::

  >>> print [t for t in threading.enumerate()
  ...        if t.getName().startswith('p01.remote.')]
  []
