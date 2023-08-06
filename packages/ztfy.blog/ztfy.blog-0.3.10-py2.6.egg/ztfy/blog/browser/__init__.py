### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.jqueryui.browser import jquery, jquery_alerts, jquery_tools
from ztfy.skin import ztfy_skin


library = Library('ztfy.blog', 'resources')

ztfy_blog_common = Resource(library, 'js/ztfy.blog.common.js', minified='js/ztfy.blog.common.min.js',
                            depends=[jquery])

ztfy_blog_front = Resource(library, 'js/ztfy.blog.front.js', minified='js/ztfy.blog.front.min.js',
                           depends=[ztfy_blog_common])

ztfy_blog_back_css = Resource(library, 'css/ztfy.blog.back.css', minified='css/ztfy.blog.back.min.css',
                              depends=[ztfy_skin])

ztfy_blog_back = Resource(library, 'js/ztfy.blog.back.js', minified='js/ztfy.blog.back.min.js',
                          depends=[ztfy_blog_common, ztfy_blog_back_css, jquery_alerts, jquery_tools])
