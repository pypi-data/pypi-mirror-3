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
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds
from zope.publisher.browser import NotFound

# import local interfaces
from ztfy.blog.browser.interfaces import IDefaultView, IBlogAddFormMenuTarget
from ztfy.blog.browser.interfaces.container import IStatusColumn, IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.browser.interfaces.container import IContainerBaseView, IContainerTableViewStatusCell
from ztfy.blog.browser.interfaces.skin import IEditFormButtons, IBlogIndexView
from ztfy.blog.browser.topic import ITopicAddFormMenuTarget
from ztfy.blog.interfaces import ISkinnable, IBaseContentRoles
from ztfy.blog.interfaces.blog import IBlog, IBlogInfo
from ztfy.blog.interfaces.topic import ITopicContainer
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogBackLayer

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.container import ContainerBaseView
from ztfy.blog.browser.skin import BaseAddForm, BaseEditForm, BaseDialogSimpleEditForm, \
                                   BasePresentationEditForm, BaseIndexView, SkinSelectWidgetFactory
from ztfy.blog.blog import Blog
from ztfy.jqueryui.browser import jquery_multiselect
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.utils.unicode import translateString

from ztfy.blog import _


class BlogDefaultViewAdapter(object):

    adapts(IBlogInfo, IZTFYBlogBackLayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@contents.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class BlogAddFormMenu(MenuItem):
    """Blogs container add form menu"""

    title = _(" :: Add blog...")


class BlogContainerContentsViewCellActions(object):

    adapts(IBlog, IZTFYBlogLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        if not IBlog(self.context).topics:
            klass = "ui-workflow ui-icon ui-icon-trash"
            intids = getUtility(IIntIds)
            return '''<span class="%s" title="%s" onclick="$.ZBlog.container.remove(%s,this);"></span>''' % (klass,
                                                                                                             translate(_("Delete blog"), context=self.request),
                                                                                                             intids.register(self.context))
        return ''


class BlogTopicsContentsView(ContainerBaseView):
    """Blog contents view"""

    implements(ITopicAddFormMenuTarget)

    legend = _("Blog's topics")
    cssClasses = { 'table': 'orderable',
                   'tr':    'topic' }

    sortOn = None
    sortOrder = None

    @property
    def values(self):
        return ITopicContainer(self.context).topics


class BlogTableViewCellStatus(object):

    adapts(IBlogInfo, IZTFYBlogBackLayer, IContainerBaseView, IStatusColumn)
    implements(IContainerTableViewStatusCell)

    def __init__(self, context, request, view, table):
        self.context = context
        self.request = request
        self.view = view
        self.table = table

    @property
    def content(self):
        return translate(_("&raquo; %d topic(s)"), context=self.request) % len(self.context.topics)


class BlogAddForm(BaseAddForm):

    implements(IBlogAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new blog")

    fields = field.Fields(IBlogInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    def updateWidgets(self):
        super(BlogAddForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    def create(self, data):
        blog = Blog()
        blog.shortname = data.get('shortname', {})
        return blog

    def add(self, blog):
        language = II18n(self.context).getDefaultLanguage()
        name = translateString(blog.shortname.get(language), forceLower=True, spaces='-')
        ids = list(self.context.keys()) + [name, ]
        self.context[name] = blog
        self.context.updateOrder(ids)

    def nextURL(self):
        return '%s/@@contents.html' % absoluteURL(self.context, self.request)


class BlogEditForm(BaseEditForm):

    legend = _("Blog properties")

    fields = field.Fields(IBlogInfo, ISkinnable)
    fields['skin'].widgetFactory = SkinSelectWidgetFactory

    buttons = button.Buttons(IEditFormButtons)

    def updateWidgets(self):
        super(BlogEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(BlogEditForm, self).handleApply(self, action)

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class BlogRolesMenuItem(JsMenuItem):
    """Blog roles menu item"""

    title = _(":: Roles")

    def update(self):
        ztfy_security.need()
        jquery_multiselect.need()
        super(BlogRolesMenuItem, self).update()


class BlogRolesEditForm(BaseDialogSimpleEditForm, RolesEditForm):

    interfaces = (IBaseContentRoles,)
    layout = getLayoutTemplate()
    parent_interface = IBlog


class BlogPresentationEditForm(BasePresentationEditForm):
    """Blog presentation edit form"""

    legend = _("Edit blog presentation properties")

    parent_interface = IBlog


class BaseBlogIndexView(BaseIndexView):
    """Base blog index view"""

    implements(IBlogIndexView)

    def update(self):
        if not self.context.visible:
            raise NotFound(self.context, 'index.html', self.request)
        super(BaseBlogIndexView, self).update()
        self.topics = self.context.getVisibleTopics()
