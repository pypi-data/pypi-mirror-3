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

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine

# import local packages

from ztfy.blog import _


class IDefaultView(Interface):
    """Interface used to get object's default view name"""

    viewname = TextLine(title=_("View name"),
                        description=_("Name of the default view for the adapter object and request"),
                        required=True,
                        default=u'@@index.html')

    def getAbsoluteURL():
        """Get full absolute URL of the default view"""


class IContainedDefaultView(IDefaultView):
    """Interface used to get object's default view name while displayed inside a container"""


class ISiteManagerTreeView(Interface):
    """Marker interface for site manager tree view"""


class ISiteManagerTreeViewContent(Interface):
    """Interface for site manager tree view contents"""

    resourceLibrary = Attribute(_("Resource library"))

    cssClass = Attribute(_("CSS class"))


class IContainerAddFormMenuTarget(Interface):
    """Marker interface for base add form menu item"""


class IMainContentAddFormMenuTarget(IContainerAddFormMenuTarget):
    """Marker interface for main content add form menu item"""


class IBlogAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for blog add menu item"""


class ISectionAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for section add form menu"""


class ITopicAddFormMenuTarget(IMainContentAddFormMenuTarget):
    """Marker interface for topic add menu item"""


class ITopicElementAddFormMenuTarget(IContainerAddFormMenuTarget):
    """Marker interface for topic element add menu item"""


class IPropertiesEditFormMenuTarget(Interface):
    """Marker interface for properties menu target"""
