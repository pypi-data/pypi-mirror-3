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
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView, ITopicElementAddFormMenuTarget
from ztfy.blog.browser.interfaces.container import IContainerBaseView
from ztfy.blog.browser.interfaces.container import IActionsColumn
from ztfy.blog.browser.interfaces.container import IContainerTableViewActionsCell
from ztfy.blog.interfaces.paragraph import IParagraphContainer, IParagraph
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.container import OrderedContainerBaseView
from ztfy.blog.browser.skin import BaseDialogAddForm, BaseDialogEditForm
from ztfy.i18n.browser import ztfy_i18n
from ztfy.skin.menu import MenuItem

from ztfy.blog import _


class ParagraphContainerContentsViewMenu(MenuItem):
    """Paragraphs container contents menu"""

    title = _("Paragraphs")


class ParagraphContainerContentsView(OrderedContainerBaseView):

    implements(ITopicElementAddFormMenuTarget)

    legend = _("Container's paragraphs")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return IParagraphContainer(self.context).paragraphs

    def render(self):
        ztfy_i18n.need()
        return super(ParagraphContainerContentsView, self).render()


class ParagraphContainerTableViewCellActions(object):

    adapts(IParagraph, IZTFYBlogLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        intids = getUtility(IIntIds)
        return '''<span class="%s" title="%s" onclick="$.ZBlog.container.remove(%s,this);"></span>''' % (klass,
                                                                                                         translate(_("Delete paragraph"), context=self.request),
                                                                                                         intids.register(self.context))


class ParagraphDefaultViewAdapter(object):

    adapts(IParagraph, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '''javascript:$.ZBlog.dialog.open('%s/%s')''' % (absoluteURL(self.context, self.request), self.viewname)


class BaseParagraphAddForm(BaseDialogAddForm):
    """Base paragraph add form"""

    implements(ITopicElementAddFormMenuTarget)

    title = _("New paragraph")
    legend = _("Adding new paragraph")

    layout = getLayoutTemplate()
    parent_interface = IParagraphContainer
    parent_view = OrderedContainerBaseView

    def add(self, paragraph):
        id = 1
        while str(id) in self.context.keys():
            id += 1
        name = str(id)
        ids = list(self.context.keys()) + [name, ]
        self.context[name] = paragraph
        self.context.updateOrder(ids)


class BaseParagraphEditForm(BaseDialogEditForm):
    """Base paragraph edit form"""

    legend = _("Edit paragraph properties")

    layout = getLayoutTemplate()
    parent_interface = IParagraphContainer
    parent_view = OrderedContainerBaseView
