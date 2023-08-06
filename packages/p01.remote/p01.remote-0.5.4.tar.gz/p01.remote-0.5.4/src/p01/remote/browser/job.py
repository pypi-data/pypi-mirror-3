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

from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.template.template import getPageTemplate

_ = zope.i18nmessageid.MessageFactory('p01')


class JobDetail(BrowserPage):
    """A simple job detail view."""

    def __call__(self):
        return zope.i18n.translate(_(u'No detail available'),
            context=self.request)


class JobProcessFrom(form.Form):

    template = getPageTemplate(name='subform')

    label = _('Process Job')
    _remoteProcessor = None

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Job successfully added for processing')
    noProcessingMessage = _('Job was not added for processing.')

    fields = field.Fields()

    @property
    def remoteProcessor(self):
        if self._remoteProcessor is None:
            self._remoteProcessor = self.context.__parent__
        return self._remoteProcessor

    def processJob(self, data):
        # this will add a new job to the remote processor queue which get
        # processed by our worker thread later.
        return self.remoteProcessor.processJob(self.context.__name__, data)

    @button.buttonAndHandler(_('Process'), name='process')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        jobid = self.processJob(data)
        if jobid:
            successMessage = _(
                'Job $name successfully added for processing with id $jobid.',
                mapping={'name': self.context.__name__, 'jobid':jobid})
            self.status = successMessage
        else:
            self.status = self.noProcessingMessage

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())
