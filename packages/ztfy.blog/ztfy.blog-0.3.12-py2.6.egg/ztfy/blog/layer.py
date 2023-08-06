### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from jquery.layer import IJQueryJavaScriptBrowserLayer
from z3c.jsonrpc.layer import IJSONRPCLayer

# import local interfaces
from ztfy.skin.layer import IZTFYBrowserLayer
from ztfy.skin.skin import IZTFYBrowserSkin

# import Zope3 packages

# import local packages


class IZTFYBlogLayer(IZTFYBrowserLayer, IJQueryJavaScriptBrowserLayer, IJSONRPCLayer):
    """Base ZTFY blog browser layer"""


class IZTFYBlogFrontLayer(IZTFYBlogLayer):
    """ZTFY browser layer for front-office pages"""


class IZTFYBlogBackLayer(IZTFYBlogLayer):
    """ZTFY browser layer for back-office pages"""


class IZTFYBlogSkin(IZTFYBrowserSkin, IZTFYBlogLayer):
    """Base ZTFY blog browser skin"""


class IZTFYBlogFrontSkin(IZTFYBlogSkin, IZTFYBlogFrontLayer):
    """ZTFY browser skin for front-office pages"""


class IZTFYBlogBackSkin(IZTFYBlogSkin, IZTFYBlogBackLayer):
    """ZTFY browser skin for back-office pages"""
