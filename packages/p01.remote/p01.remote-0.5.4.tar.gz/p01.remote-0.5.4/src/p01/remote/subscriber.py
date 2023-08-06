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

import zope.component
import zope.lifecycleevent.interfaces

from p01.remote import interfaces


# object modified for
@zope.component.adapter(interfaces.ISchedulerItem,
                        zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def objectModifiedSubscriber(item, event):
    """Event subscriber for re-schedule ISchedulerItem."""
    item.__parent__.reScheduleItem(item)
