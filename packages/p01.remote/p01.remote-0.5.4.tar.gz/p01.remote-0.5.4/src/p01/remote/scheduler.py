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

import time
import calendar
import persistent
import persistent.list
from BTrees.IOBTree import IOBTree

import zope.interface
from zope.container import contained

from zope.schema.fieldproperty import FieldProperty

from p01.remote import interfaces


incSeconds = lambda t: 1
incMinutes = lambda t: 60
incHours = lambda t: 60*60
incDays = lambda t: 24*60*60
def incMonth(t):
    mlen = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    m = time.gmtime(t)[1] - 1
    if m == 1:
        # see if we have a leap year
        y = time.gmtime(t)[0]
        if y % 4 != 0:
            d = 28
        elif y % 400 == 0:
            d = 29
        elif y % 100 == 0:
            d = 28
        else:
            d = 29
        return d*24*60*60
    return mlen[m]*24*60*60


def adjustCallTime(cron, t):
    localtime = time.gmtime(t)
    l = list(localtime)
    if cron.minute:
        l[5] = 0
    elif cron.hour:
        l[4] = 0
    elif cron.dayOfMonth:
        l[3] = 1
    elif cron.dayOfWeek:
        l[7] = 0
    elif cron.month:
        l[2] = 1
    return int(calendar.timegm(l))


# TODO: change _items to an OOBTree and add migration. This allows us to provide
#       valid names, right know we assign int instead of unicode
class Scheduler(contained.Contained, persistent.Persistent):
    """Scheduler container."""

    zope.interface.implements(interfaces.IScheduler)

    def __init__(self):
        super(Scheduler, self).__init__()
        self._counter = 0
        self._items = IOBTree()
        self._pending = persistent.list.PersistentList()

    def reset(self):
        self._pending = persistent.list.PersistentList()

    @property
    def remoteProcessor(self):
        return self.__parent__

# TODO: only locate if not located
# TODO: use counter only if no __name__ is gven for generate key
# TODO: use while and check if the key is allready in use
    def add(self, item):
        key = self._counter = self._counter + 1
        self._items[key] = item
        item.__name__ = key

    def remove(self, item):
        del self._items[item.__name__]
        # remove scheduled item from pending list
        if item in self._pending:
            self._pending.remove(item)

    def __contains__(self, key):
        return key in self.keys()

    def get(self, key):
        return self._items.get(key)

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def reScheduleItem(self, item, callTime=None):
        if callTime is None:
            callTime = int(time.time())
        if item in self._pending:
            # remove scheduled item
            self._pending.remove(item)
        # calculate next call time, but first make sure we reset nextCallTime
        # to a smaller value then the used callTime
        item.nextCallTime = 0
        nextCallTime = item.getNextCallTime(callTime)
        # only add items with next call time but not for duplicated jobs
        if nextCallTime and nextCallTime <= callTime and \
            not item.jobName in [i.jobName for i in self._pending]:
            self._pending.append(item)

    def reScheduleItems(self, callTime=None):
        if callTime is None:
            callTime = int(time.time())
        for item in self.values():
            self.reScheduleItem(item)

    def updatePending(self, callTime):
        for item in self.values():
            # skip already scheduled items
            if item in self._pending:
                # this will prevent to process more then once
                continue
            # calculate next call time if not pending
            nextCallTime = item.getNextCallTime(callTime)
            # only add items with next call time but not for duplicated jobs
            if nextCallTime and nextCallTime <= callTime and \
                not item.jobName in [i.jobName for i in self._pending]:
                self._pending.append(item)

    def pullNextSchedulerItem(self, now=None):
        """Get next pending job based on the current time."""
        if now is None:
            now = int(time.time())
        if not self._pending:
            # calculate new scheduled items if pending is empty
            self.updatePending(now)
        # get first scheduled item in pending list which has a smaller next
        # call time then now and can get it's job by the jobName
        while self._pending:
            return self._pending.pop(0)
        # return None if no job get found based on scheduler item or pending
        # list is empty
        return None


class Cron(contained.Contained, persistent.Persistent):
    """A cron scheduler item."""

    zope.interface.implements(interfaces.ICron)

    jobName = FieldProperty(interfaces.ICron['jobName'])
    input = FieldProperty(interfaces.ICron['input'])
    active = FieldProperty(interfaces.ICron['active'])

    minute = FieldProperty(interfaces.ICron['minute'])
    hour = FieldProperty(interfaces.ICron['hour'])
    dayOfMonth = FieldProperty(interfaces.ICron['dayOfMonth'])
    month = FieldProperty(interfaces.ICron['month'])
    dayOfWeek = FieldProperty(interfaces.ICron['dayOfWeek'])

    nextCallTime = FieldProperty(interfaces.ICron['nextCallTime'])

    def __init__(self, jobName, minute=None, hour=None, dayOfMonth=None,
        month=None, dayOfWeek=None, active=True, startTime=None):
        super(Cron, self).__init__()
        self.jobName = jobName
        self.active = active
        self.minute = minute
        self.hour = hour
        self.dayOfMonth = dayOfMonth
        self.month = month
        self.dayOfWeek = dayOfWeek
        if startTime is None:
            startTime = int(time.time())
        self.nextCallTime = startTime

    def getNextCallTime(self, callTime):
        """Return next call time.

        Note ``next`` means not that the result must be in the future. It could
        be or not. It's just the next call time calculated if by the ``last``
        getNextCallTime call. The nextCallTime value is caching this last call
        value.

        How does this work:

        If the next call time is before the given call time, calculate the
        next call time and return the previous next call time. If the next
        call time is after the call time, return the stored next call time.

        This will ensure that we never miss a call between the last call time
        and the current call time. This concept does not only ensure that we
        skip more the one missed call between the last call time and the next
        call time. This will also ensure that we do not too often calculate the
        next call time. We only calculate the next call time if absolutly
        needed.

        """
        if self.nextCallTime <= callTime:
            currentNextCallTime = self.nextCallTime
            next = adjustCallTime(self, callTime)

            # setup increase methods
            inc = incSeconds
            if self.minute:
                # increase in minutes for catch first minute
                inc = incMinutes
            elif self.hour:
                # increase in hours for catch first hour
                inc = incHours
            elif self.dayOfMonth:
                # increase in days for catch first day of month
                inc = incDays
            elif self.dayOfWeek:
                # increase in days for catch first day of week
                inc = incDays
            elif self.month:
                # increase in month for catch first month
                inc = incMonth

            while next <= callTime+365*24*60*60:
                incamount = inc(next)
                next += incamount
                fields = time.gmtime(next)
                # setup default values for each field
                minute = self.minute or range(60)
                hour = self.hour or range(24)
                month = self.month or range(1, 13)
                dayOfWeek = self.dayOfWeek or range(7)
                dayOfMonth = self.dayOfMonth or range(1, 32)
                if ((fields[1] in month) and
                    (fields[2] in dayOfMonth) and
                    (fields[3] in hour) and
                    (fields[4] in minute) and
                    (fields[6] % 7 in dayOfWeek)):
                    self.nextCallTime = next
                    break

            return currentNextCallTime
        return self.nextCallTime

    def __repr__(self):
        return '<%s %s for: %r>' %(self.__class__.__name__, self.__name__,
            self.jobName)


class Delay(contained.Contained, persistent.Persistent):
    """A delay definition for scheduled jobs."""
    zope.interface.implements(interfaces.IDelay)

    jobName = FieldProperty(interfaces.IDelay['jobName'])
    active = FieldProperty(interfaces.IDelay['active'])
    input = FieldProperty(interfaces.IDelay['input'])
    delay = FieldProperty(interfaces.IDelay['delay'])
    nextCallTime = FieldProperty(interfaces.IDelay['nextCallTime'])

    def __init__(self, jobName, delay=0, active=True, startTime=None):
        super(Delay, self).__init__()
        self.jobName = jobName
        self.active = active
        self.delay = delay
        if startTime is None:
            startTime = int(time.time())
        self.nextCallTime = self.getNextCallTime(startTime)

    def getNextCallTime(self, callTime):
        if self.active and self.delay and self.nextCallTime <= callTime:
                # callculate the next call time and cache it
                currentNextCallTime = self.nextCallTime
                # set the new next call time
                self.nextCallTime = callTime + self.delay
                # if initial nextCallTime was 0 (zero) return new calculated
                # next call time.
                return currentNextCallTime or self.nextCallTime
        return self.nextCallTime

    def __repr__(self):
        return '<%s %s for: %r>' %(self.__class__.__name__, self.__name__,
            self.jobName)
