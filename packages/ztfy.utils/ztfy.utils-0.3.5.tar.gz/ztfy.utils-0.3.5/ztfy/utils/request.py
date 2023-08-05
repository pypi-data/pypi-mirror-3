### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.publisher.interfaces import IRequest
from zope.annotation.interfaces import IAnnotations

# import local interfaces

# import Zope3 packages
from zope.security.management import getInteraction

# import local packages

from ztfy.utils import _
from zope.security.interfaces import NoInteraction


def getRequest():
    """Extract request from current interaction"""
    interaction = getInteraction()
    for participation in interaction.participations:
        if IRequest.providedBy(participation):
            return participation
    raise RuntimeError, _("No Request in interaction !")


def queryRequest():
    try:
        return getRequest()
    except NoInteraction:
        return None


def getRequestPrincipal(request=None):
    """Get principal from given request"""
    if request is None:
        request = getRequest()
    return request.principal

getPrincipal = getRequestPrincipal


def getRequestAnnotations(request=None):
    """Get annotations from given request"""
    if request is None:
        request = getRequest()
    return IAnnotations(request)

getAnnotations = getRequestAnnotations


def getRequestData(key, request=None, default=None):
    """Get request data, stored into request annotations"""
    try:
        annotations = getRequestAnnotations(request)
        return annotations.get(key, default)
    except:
        return default

getData = getRequestData


def setRequestData(key, data, request=None):
    """Define request data, stored into request annotations"""
    annotations = getRequestAnnotations(request)
    annotations[key] = data

setData = setRequestData
