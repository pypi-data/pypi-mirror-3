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

import transaction
import zope.interface
import zope.publisher.base
import zope.security.management
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import traverse
from zope.app.publication import zopepublication
from zope.security.interfaces import IPrincipal

from p01.remote import interfaces


class RemoteProcessorPrincipal(object):
    """Remote processor principal."""

    zope.interface.implements(IPrincipal)

    id = 'p01.remote.principal'
    title = 'Remote Queue Principal'
    description = 'Principal used in a WorkerPublications.'


# expose our remote processor principal
remoteProcessorPrincipal = RemoteProcessorPrincipal()


class WorkerPublication(zopepublication.ZopePublication):
    """A custom publication to process the next job."""

    zope.interface.implements(interfaces.IWorkerPublication)

    def beforeTraversal(self, request):
        # Instead of use the authentication just set our principal.
        request.setPrincipal(remoteProcessorPrincipal)
        zope.security.management.newInteraction(request)
        transaction.begin()

    def traverseName(self, request, ob, name):
        # Provide a very simple traversal mechanism. We assume that the 
        # worker is allowed to do everything. Note that the DB is not 
        # exposed to the job callable.
        return traverse(removeSecurityProxy(ob), name, None)


class WorkerRequest(zope.publisher.base.BaseRequest):
    """A custom publisher request for the worker."""

    zope.interface.implements(interfaces.IWorkerRequest)

    def __init__(self, *args):
        super(WorkerRequest, self).__init__(None, {}, positional=args)
