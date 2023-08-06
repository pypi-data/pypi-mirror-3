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

import zope.i18n
import zope.i18nmessageid
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL

from z3c.form import field
from z3c.form import button
from z3c.form import term
from z3c.form.browser.select import SelectFieldWidget
from z3c.formui import form
from z3c.template.template import getPageTemplate

from p01.remote import interfaces
from p01.remote import scheduler

_ = zope.i18nmessageid.MessageFactory('p01')


class DelaySchedulerDetail(BrowserPage):
    """A simple delay scheduler detail view."""

    def __call__(self):
        return zope.i18n.translate(_(u'Delay Scheduler'), context=self.request)


class CronSchedulerDetail(BrowserPage):
    """A simple cron scheduler detail view."""

    def __call__(self):
        return zope.i18n.translate(_(u'Cron Scheduler'), context=self.request)


class CronSchedulerAddFrom(form.AddForm):
    """Cron scheduler job add form."""

    zope.interface.implements(interfaces.IJobNameTermsAware)

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Cron scheduler')

    fields = field.Fields(interfaces.ICron).select(
        'jobName', 'hour', 'minute', 'dayOfMonth', 'month', 'dayOfWeek',
        'active')

    # cheat a little bit and use a vocabulary based on JobNameTerms
    fields['jobName'].widgetFactory = SelectFieldWidget

    def createAndAdd(self, data):
        jobName = data['jobName']
        hour = data['hour']
        minute = data['minute']
        dayOfMonth = data['dayOfMonth']
        month = data['month']
        dayOfWeek = data['dayOfWeek']
        active = data['active']
        cron = scheduler.Cron(jobName, minute, hour, dayOfMonth, month,
            dayOfWeek, active)
        jobid = self.context.addScheduler(cron)
        self._finishedAdd = True
        return jobid

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/scheduler.html' % absoluteURL(self.context, self.request)


class CronSchedulerEditFrom(form.EditForm):
    """Cron scheduler job edit form."""

    zope.interface.implements(interfaces.IJobNameTermsAware)

    template = getPageTemplate(name='subform')

    label = _('Edit Cron scheduler')

    buttons = form.EditForm.buttons.copy()
    handlers = form.EditForm.handlers.copy()

    fields = field.Fields(interfaces.ICron).select(
        'jobName', 'hour', 'minute', 'dayOfMonth', 'month', 'dayOfWeek',
        'active')

    # cheat a little bit and use a vocabulary based on JobNameTerms
    fields['jobName'].widgetFactory = SelectFieldWidget

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())


class DelaySchedulerAddFrom(form.AddForm):
    """Delay scheduler job add form."""

    zope.interface.implements(interfaces.IJobNameTermsAware)

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Delay scheduler')

    fields = field.Fields(interfaces.IDelay).select('jobName', 'delay')

    # cheat a little bit and use a vocabulary based on JobNameTerms
    fields['jobName'].widgetFactory = SelectFieldWidget

    def createAndAdd(self, data):
        jobName = data['jobName']
        delay = data['delay']
        job = scheduler.Delay(jobName, delay)
        jobid = self.context.addScheduler(job)
        self._finishedAdd = True
        return jobid

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/scheduler.html' % absoluteURL(self.context, self.request)


class DelaySchedulerEditFrom(form.EditForm):
    """Delay scheduler job edit form."""

    zope.interface.implements(interfaces.IJobNameTermsAware)

    template = getPageTemplate(name='subform')

    label = _('Edit Delay scheduler')

    buttons = form.EditForm.buttons.copy()
    handlers = form.EditForm.handlers.copy()

    fields = field.Fields(interfaces.IDelay).select('jobName', 'delay')

    # cheat a little bit and use a vocabulary based on JobNameTerms
    fields['jobName'].widgetFactory = SelectFieldWidget

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())
