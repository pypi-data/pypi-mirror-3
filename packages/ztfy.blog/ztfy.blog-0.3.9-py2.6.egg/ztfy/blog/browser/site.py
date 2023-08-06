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
from z3c.table.interfaces import INoneCell
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView, ISiteManagerTreeView, ISiteManagerTreeViewContent, IBlogAddFormMenuTarget, ISectionAddFormMenuTarget
from ztfy.blog.browser.interfaces.container import IContainerBaseView, ITitleColumn, IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.browser.interfaces.container import IContainerTableViewTitleCell
from ztfy.blog.browser.interfaces.skin import IEditFormButtons, ISiteManagerIndexView
from ztfy.blog.interfaces import IBaseContent, IBaseContentRoles, ISkinnable
from ztfy.blog.interfaces.blog import IBlog
from ztfy.blog.interfaces.section import ISection
from ztfy.blog.interfaces.site import ISiteManager, ISiteManagerInfo, \
                                      ITreeViewContents
from ztfy.blog.interfaces.topic import ITopic
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.container import ContainerBaseView, OrderedContainerBaseView
from ztfy.blog.browser.skin import BaseDialogSimpleEditForm, BaseEditForm, BasePresentationEditForm, \
                                   BaseIndexView, SkinSelectWidgetFactory
from ztfy.jqueryui.browser import jquery_treetable, jquery_multiselect, jquery_ui_base
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem

from ztfy.blog import _


class SiteManagerTreeViewMenu(MenuItem):
    """Site manager tree view menu"""

    title = _("Tree view")


def getValues(parent, context, output):
    output.append((parent, context))
    contents = ITreeViewContents(context, None)
    if contents is not None:
        for item in contents.values:
            getValues(context, item, output)


class SiteManagerTreeView(ContainerBaseView):
    """Site manager tree view"""

    implements(ISiteManagerTreeView)

    sortOn = None
    cssClasses = { 'table': 'orderable treeview' }

    def __init__(self, context, request):
        super(SiteManagerTreeView, self).__init__(context, request)
        self.intids = getUtility(IIntIds)

    @property
    def values(self):
        result = []
        getValues(None, self.context, result)
        return result

    def renderRow(self, row, cssClass=None):
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = '%s %s' % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        (parent, context), _col, _colspan = row[0]
        content = ISiteManagerTreeViewContent(context, None)
        if (content is not None) and content.resourceLibrary:
            content.resourceLibrary.need()
        if (content is not None) and content.cssClass:
            cssClass += ' %s' % content.cssClass
        else:
            if ISiteManager.providedBy(context):
                cssClass += ' site'
            elif IBlog.providedBy(context):
                cssClass += ' blog'
            elif ISection.providedBy(context):
                cssClass += ' section'
            elif ITopic.providedBy(context):
                cssClass += ' topic'
        if parent is not None:
            cssClass += ' child-of-node-%d' % self.intids.register(parent)
        id = 'id="node-%d"' % self.intids.register(context)
        cssClass = self.getCSSClass('tr', cssClass)
        cells = [self.renderCell(context, col, colspan)
                 for (parent, context), col, colspan in row]
        return u'\n    <tr %s%s>%s\n    </tr>' % (id, cssClass, u''.join(cells))

    def renderCell(self, item, column, colspan=0):
        if INoneCell.providedBy(column):
            return u''
        cssClass = column.cssClasses.get('td')
        cssClass = self.getCSSClass('td', cssClass)
        colspanStr = colspan and ' colspan="%s"' % colspan or ''
        return u'\n      <td%s%s>%s</td>' % (cssClass, colspanStr, column.renderCell(item))

    def update(self):
        super(SiteManagerTreeView, self).update()
        jquery_treetable.need()
        jquery_ui_base.need()


class SiteManagerTreeViewTitleColumnCellAdapter(object):

    adapts(IBaseContent, IZTFYBlogLayer, ISiteManagerTreeView, ITitleColumn)
    implements(IContainerTableViewTitleCell)

    prefix = u''
    after = u''
    suffix = u''

    def __init__(self, context, request, table, column):
        self.context = context
        self.request = request
        self.table = table
        self.column = column

    @property
    def before(self):
        return '<span class="ui-icon"></span>'


class SiteManagerContentsView(OrderedContainerBaseView):
    """Site manager contents view"""

    implements(IBlogAddFormMenuTarget, ISectionAddFormMenuTarget)

    legend = _("Site's content")
    cssClasses = { 'table': 'orderable' }

    @property
    def values(self):
        return ISiteManager(self.context).values()


class SiteManagerContentsViewCellActions(object):

    adapts(ISiteManager, IZTFYBlogLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        return u''


class SiteManagerEditForm(BaseEditForm):

    legend = _("Site manager properties")

    fields = field.Fields(ISiteManagerInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    buttons = button.Buttons(IEditFormButtons)

    def updateWidgets(self):
        super(SiteManagerEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(SiteManagerEditForm, self).handleApply(self, action)

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class SiteManagerRolesMenuItem(JsMenuItem):
    """Site manager roles menu item"""

    title = _(":: Roles")

    def update(self):
        ztfy_security.need()
        jquery_multiselect.need()
        super(SiteManagerRolesMenuItem, self).update()


class SiteManagerRolesEditForm(BaseDialogSimpleEditForm, RolesEditForm):

    interfaces = (IBaseContentRoles,)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager


class SiteManagerPresentationEditForm(BasePresentationEditForm):
    """Site manager presentation edit form"""

    legend = _("Edit site presentation properties")

    parent_interface = ISiteManager


class SiteManagerDefaultViewAdapter(object):

    adapts(ISiteManager, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@treeview.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class SiteManagerTreeViewDefaultViewAdapter(SiteManagerDefaultViewAdapter):

    adapts(ISiteManager, IZTFYBlogBackLayer, ISiteManagerTreeView)
    implements(IDefaultView)

    @property
    def viewname(self):
        return '@@properties.html'


class BaseSiteManagerIndexView(BaseIndexView):
    """Base site manager index view"""

    implements(ISiteManagerIndexView)
