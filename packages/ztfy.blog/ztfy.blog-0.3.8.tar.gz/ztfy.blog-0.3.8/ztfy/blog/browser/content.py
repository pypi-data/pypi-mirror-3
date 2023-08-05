### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView, IContainedDefaultView
from ztfy.blog.interfaces import IBaseContent
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages


class BaseContentDefaultViewAdapter(object):

    adapts(IBaseContent, IZTFYBlogLayer, Interface)
    implements(IDefaultView)

    viewname = ''

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return absoluteURL(self.context, self.request)


class BaseContentDefaultBackViewAdapter(object):

    adapts(IBaseContent, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class BaseContainedDefaultBackViewAdapter(object):

    adapts(IOrderedContainer, IZTFYBlogBackLayer, Interface)
    implements(IContainedDefaultView)

    viewname = '@@contents.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)
