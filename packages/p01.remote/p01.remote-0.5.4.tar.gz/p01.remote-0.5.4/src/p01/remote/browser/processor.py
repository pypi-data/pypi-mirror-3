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

import pytz
import datetime
import transaction

import zope.component
import zope.i18nmessageid
from zope.security.proxy import removeSecurityProxy

import z3c.tabular.table
from z3c.table import column
from z3c.form import button
from z3c.formui import form

import p01.remote.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class IDCheckBoxColumn(column.CheckBoxColumn):
    """CheckBox column by id."""

    def getSortKey(self, item):
        return unicode(item.id)

    def getItemValue(self, item):
        return unicode(item.id)


class IDColumn(column.Column):
    """ID column."""

    header = _('ID')

    def renderCell(self, item):
        return unicode(item.id)


class NameColumn(column.Column):
    """Name column."""

    header = _('Name')

    def renderCell(self, item):
        return item.__name__


class DetailColumn(column.Column):
    """Job detail view column."""

    header = _('Detail')

    def renderCell(self, item):
        view = zope.component.getMultiAdapter((item, self.request),
            name='detail')
        return view()


class StatusColumn(column.Column):
    """Status column."""

    header = _('Status')

    def renderCell(self, item):
        return item.status

class DateColumn(column.Column):

    attrName = None

    def renderCell(self, item):
        value = getattr(item, self.attrName, None)
        if value is None:
            return ''
        return value.isoformat(' ')


class Processor(z3c.tabular.table.SubFormTable):
    """Jobs processing management page for IRemoteProcessor."""

    label = _('Jobs')
    formErrorsMessage = _('There were some errors.')
    noSelectedItemsMessage = _('No jobs selected, please select a checkbox.')
    ignoreContext = True
    allowDelete = False
    errors  = []
    _remoteProcessor = None
    _processor = None

    subFormName = u'edit'

    def setUpColumns(self):
        return [
            column.addColumn(self, IDCheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, IDColumn, u'id',
                             weight=2),
            column.addColumn(self, NameColumn, u'name',
                             weight=3),
            column.addColumn(self, StatusColumn, u'status',
                             weight=4),
            column.addColumn(self, DetailColumn, u'detail',
                             weight=5),
            column.addColumn(self, DateColumn, u'started',
                             weight=6,
                             header=_(u'Started'),
                             attrName='started'),
            column.addColumn(self, DateColumn, u'completed',
                             weight=7,
                             header=_(u'Completed'),
                             attrName='completed'),
            ]

    @property
    def remoteProcessor(self):
        if self._remoteProcessor is None:
            self._remoteProcessor = self.context
        return self._remoteProcessor

    @property
    def processor(self):
        if self._processor is None:
            trusted = removeSecurityProxy(self.remoteProcessor)
            self._processor = trusted._processor
        return self._processor

    @property
    def values(self):
        return self.processor.values()

    @property
    def isProcessing(self):
        return self.remoteProcessor.isProcessing

    def _removeJobs(self, stati=None):
        """Remove jobs with given status or all."""
        jobs = len(list(self.processor.keys()))
        self.remoteProcessor.removeJobs(stati)
        cleaned = jobs - len(list(self.processor.keys()))
        current = jobs - cleaned
        self.status = _(u'Removed ${removed} jobs, skipped ${current} jobs.',
            mapping={'removed': cleaned, 'current': current})

    @button.buttonAndHandler(u'Remove error', name='removeError')
    def _handleRemoveERROR(self, action):
        """Remove all completed jobs."""
        self._removeJobs(p01.remote.interfaces.ERROR)
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Remove cancelled', name='removeCancelled')
    def _handleRemoveCancelled(self, action):
        """Remove all completed jobs."""
        self._removeJobs(p01.remote.interfaces.CANCELLED)
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Remove completed', name='removeCompleted')
    def _handleRemoveCompleted(self, action):
        """Remove all completed jobs."""
        self._removeJobs(p01.remote.interfaces.COMPLETED)
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Remove all', name='removeAll')
    def handleRemoveAll(self, action):
        """Remove all jobs."""
        self._removeJobs()
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancelSelected(self, action):
        changed = False
        if not len(self.selectedItems):
            self.status = self.noSelectedItemsMessage
            return
        for job in self.selectedItems:
            self.remoteProcessor.cancelJob(job.id)
            changed = True
        if changed:
            self.status = _(u'Jobs were successfully cancelled.')
        else:
            self.status = _(u'No jobs were selected.')
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Cancel all', name='cancelAll')
    def handleCancelAll(self, action):
        """Cancel all jobs."""
        changed = False
        jobids = list(self.processor.keys())
        for index, jobid in enumerate(jobids):
            if index%100 == 99:
                transaction.commit()
                changed = True
            self.remoteProcessor.cancelJob(jobid)
        if changed:
            self.status = _(u'All jobs cancelled')
        else:
            self.status = _(u'No jobs available for cancelling')
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Start processing', name='start',
        condition=lambda form: not form.isProcessing)
    def handleStartProcessing(self, action):
        """Start processing"""
        self.remoteProcessor.startProcessing()
        self.updateAfterActionExecution()

    @button.buttonAndHandler(u'Stop processing', name='stop',
        condition=lambda form: form.isProcessing)
    def handleStopProcessing(self, action):
        """Start processing"""
        self.remoteProcessor.stopProcessing()
        self.updateAfterActionExecution()


class NameCheckBoxColumn(column.CheckBoxColumn):
    """CheckBox column by __name__."""

    def getSortKey(self, item):
        return unicode(item.__name__)

    def getItemValue(self, item):
        return unicode(item.__name__)


def canDelete(form):
    return form.supportsDelete

class Jobs(z3c.tabular.table.SubFormTable):
    """Jobs management page for IRemoteProcessor."""

    label = _('Available Jobs')
    formErrorsMessage = _('There were some errors.')
    noSelectedItemsMessage = _('No jobs selected, please select a checkbox.')
    ignoreContext = True
    allowDelete = True
    errors  = []
    _remoteProcessor = None
    _jobs = None

    subFormName = u'process'

    def setUpColumns(self):
        return [
            column.addColumn(self, NameCheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, NameColumn, u'name',
                             weight=2),
            column.addColumn(self, DetailColumn, u'detail',
                             weight=3),
            ]

    @property
    def remoteProcessor(self):
        if self._remoteProcessor is None:
            self._remoteProcessor = self.context
        return self._remoteProcessor

    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = removeSecurityProxy(self.remoteProcessor)._jobs
        return self._jobs

    @property
    def values(self):
        return self.jobs.values()

    def executeDelete(self, item):
        del self.jobs[item.__name__]

    @button.buttonAndHandler(_('Delete'), name='delete', condition=canDelete)
    def handleDelete(self, action):
        self.doDelete(action)

    @button.buttonAndHandler(u'Process')
    def handleSubForm(self, action):
        self.doSubForm(action)

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.nextURL = self.request.getURL()


class JobNameColumn(column.Column):
    """JobName column."""

    header = _('Job Name')

    def renderCell(self, item):
        return item.jobName


class ScheduledForColumn(column.Column):
    """Schedule for column."""

    header = _('Scheduled for')

    def renderCell(self, item):
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        nextCallTime = datetime.datetime.fromtimestamp(item.nextCallTime)
        return formatter.format(nextCallTime)


class ScheduledForUTCColumn(column.Column):
    """Schedule for column."""

    header = _('Scheduled for (UTC)')

    def renderCell(self, item):
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        tz = pytz.UTC
        nextCallTime = datetime.datetime.fromtimestamp(item.nextCallTime, tz)
        return formatter.format(nextCallTime)


class Scheduler(z3c.tabular.table.SubFormTable):
    """Scheduled item management page for IRemoteProcessor."""

    buttons = z3c.tabular.table.SubFormTable.buttons.copy()
    handlers = z3c.tabular.table.SubFormTable.handlers.copy()

    label = _('Scheduled Jobs')
    formErrorsMessage = _('There were some errors.')
    noSelectedItemsMessage = _('No item selected, please select a checkbox.')
    ignoreContext = True
    allowDelete = True
    errors  = []
    _remoteProcessor = None
    _scheduler = None

    subFormName = u'edit'

    def setUpColumns(self):
        return [
            column.addColumn(self, NameCheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, NameColumn, u'name',
                             weight=2),
            column.addColumn(self, JobNameColumn, u'jobName',
                             weight=2),
            column.addColumn(self, ScheduledForColumn, u'scheduled',
                             weight=3),
            column.addColumn(self, ScheduledForUTCColumn, u'scheduledutc',
                             weight=4),
            column.addColumn(self, DetailColumn, u'detail',
                             weight=5),
            ]

    @property
    def remoteProcessor(self):
        if self._remoteProcessor is None:
            self._remoteProcessor = self.context
        return self._remoteProcessor

    @property
    def scheduler(self):
        if self._scheduler is None:
            trusted = removeSecurityProxy(self.remoteProcessor)
            self._scheduler = trusted._scheduler
        return self._scheduler

    @property
    def values(self):
        return self.scheduler.values()

    def executeDelete(self, item):
        self.scheduler.remove(item)

    @button.buttonAndHandler(u'Re-Schedule', name='reschedule')
    def handleReSchedule(self, action):
        """Re-schedule selected items"""
        changed = False
        for item in self.selectedItems:
            self.scheduler.reScheduleItem(item)
            changed = True
        if changed:
            self.status = _(u'Selected items were successfully re-scheduled.')
        else:
            self.status = self.noSelectedItemsMessage

    @button.buttonAndHandler(u'Re-Schedule (all)', name='rescheduleall')
    def handleReScheduleAll(self, action):
        """Re-schedule all items"""
        self.scheduler.reScheduleItems()
        self.status = _(u'All items were successfully re-scheduled.')
