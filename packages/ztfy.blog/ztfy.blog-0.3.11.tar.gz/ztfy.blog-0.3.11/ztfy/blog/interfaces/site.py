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
from zope.location.interfaces import ILocation, IPossibleSite

# import local interfaces
from ztfy.blog.interfaces import IBaseContent, IMainContent, IBaseContentRoles
from ztfy.blog.interfaces.blog import IBlogContainer
from ztfy.blog.interfaces.category import ICategoryManagerTarget
from ztfy.blog.interfaces.section import ISectionContainer

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface
from zope.schema import List, Object

# import local packages

from ztfy.blog import _


#
# Site management
#

class ISiteManagerInfo(IBaseContent):
    """Base site interface"""

    def getVisibleContents(request):
        """Get list of contents visible from given request"""


class ISiteManagerWriter(Interface):
    """Site writer interface"""


class ISiteManager(ISiteManagerInfo, ISiteManagerWriter, IBaseContentRoles,
                   ICategoryManagerTarget, ISectionContainer, IBlogContainer,
                   ILocation, IPossibleSite):
    """Site full interface"""

    contains(IMainContent)


class ITreeViewContents(Interface):
    """Marker interface for contents which should be displayed inside tree views"""

    values = List(title=_("Container values"),
                  value_type=Object(schema=Interface),
                  readonly=True)
