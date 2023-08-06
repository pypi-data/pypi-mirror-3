###############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.interface
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import TraversalError
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler


class processor(SimpleHandler):
    """Traversal handler for processing jobs called ++processor++.
    
    Used to traverse to a remote job.
    """

    zope.interface.implements(ITraversable)

    def traverse(self, name, ignored):
        trusted = removeSecurityProxy(self.context)
        if name:
            try:
                return trusted._processor[int(name)]
            except (KeyError, ValueError, TypeError):
                raise TraversalError(trusted, name)
        else:
            return trusted._processor


class jobs(SimpleHandler):
    """Traversal handler for available jobs called ++jobs++.
    
    Used to traverse to a remote job.
    """

    zope.interface.implements(ITraversable)

    def traverse(self, name, ignored):
        trusted = removeSecurityProxy(self.context)
        if name:
            try:
                return trusted._jobs[name]
            except (KeyError, ValueError, TypeError):
                raise TraversalError(trusted, name)
        else:
            return trusted._jobs


class scheduler(SimpleHandler):
    """Traversal handler for scheduled items called ++scheduler++.
    
    Used to traverse to a scheduler item.
    """

    zope.interface.implements(ITraversable)

    def traverse(self, name, ignored):
        trusted = removeSecurityProxy(self.context)
        if name:
            try:
                return trusted._scheduler[name]
            except (KeyError, ValueError, TypeError):
                raise TraversalError(trusted, name)
        else:
            return trusted._scheduler
