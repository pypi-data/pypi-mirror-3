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
import copy

# import Zope3 interfaces
from hurry.query.interfaces import IQuery
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.container.interfaces import IContainer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserSkinType
from zope.schema.interfaces import IText
from zope.traversing.interfaces import IBeforeTraverseEvent, TraversalError

# import local interfaces
from ztfy.blog.browser.interfaces.skin import IBaseForm, IDialogAddFormButtons, IDialogEditFormButtons, \
                                              IPresentationForm, IPresentationTarget, IBaseIndexView
from ztfy.blog.interfaces import ISkinnable
from ztfy.blog.interfaces.resource import IResourceContainerTarget
from ztfy.blog.layer import IZTFYBlogLayer, IZTFYBlogFrontLayer
from ztfy.file.browser.widget.interfaces import IHTMLWidgetSettings

# import Zope3 packages
from z3c.form import field, widget, button
from z3c.form.browser.select import SelectWidget
from z3c.formjs import ajax, jsaction
from z3c.template.template import getLayoutTemplate
from zope.component import adapter, adapts, getUtility, queryUtility, queryMultiAdapter
from zope.event import notify
from zope.interface import implements, implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import applySkin
from zope.traversing import namespace
from zope.traversing.api import getName
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.skin.form import AjaxForm, AddForm, EditForm, DialogAddForm, DialogEditForm
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.catalog.index import Text
from ztfy.utils.traversing import getParent

from ztfy.blog import _


class BaseTemplateBackView(TemplateBasedPage):

    implements(IBaseForm)

    def update(self):
        skin = queryUtility(IBrowserSkinType, 'ZMI')
        if (skin is None) or ((skin is not None) and not skin.providedBy(self.request)):
            applySkin(self.request, getUtility(IBrowserSkinType, 'ZBlog.BO'))
        super(BaseTemplateBackView, self).update()


class BaseAddForm(AddForm):

    implements(IBaseForm)

    def update(self):
        skin = queryUtility(IBrowserSkinType, 'ZMI')
        if (skin is None) or ((skin is not None) and not skin.providedBy(self.request)):
            applySkin(self.request, getUtility(IBrowserSkinType, 'ZBlog.BO'))
        super(BaseAddForm, self).update()


class BaseDialogAddForm(AjaxForm, BaseAddForm, DialogAddForm):
    """Base dialog add form"""

    buttons = button.Buttons(IDialogAddFormButtons)
    layout = None
    parent_interface = IContainer
    parent_view = None
    handle_upload = False

    @jsaction.handler(buttons['add'])
    def add_handler(self, event, selector):
        return '$.ZBlog.form.add(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZBlog.dialog.close();'

    @ajax.handler
    def ajaxCreate(self):
        # Create resources through AJAX request
        # JSON results have to be included in a textarea to handle JQuery.Form plugin file uploads
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        self.createAndAdd(data)
        parent = getParent(self.context, self.parent_interface)
        notify(ObjectModifiedEvent(parent))
        return self.getOutput(writer, parent)

    def getOutput(self, writer, parent):
        if self.parent_view is not None:
            view = self.parent_view(parent, self.request)
            view.update()
            return '<textarea>%s</textarea>' % writer.write({ 'output': u"<!-- OK -->\n" + view.output() })
        else:
            return writer.write({ 'output': u"OK" })


class BaseEditForm(EditForm):

    implements(IBaseForm)

    def update(self):
        skin = queryUtility(IBrowserSkinType, 'ZMI')
        if (skin is None) or ((skin is not None) and not skin.providedBy(self.request)):
            applySkin(self.request, getUtility(IBrowserSkinType, 'ZBlog.BO'))
        super(BaseEditForm, self).update()


class BaseDialogSimpleEditForm(AjaxForm, BaseEditForm, DialogEditForm):
    """Base dialog simple edit form"""

    buttons = button.Buttons(IDialogEditFormButtons)
    layout = None
    parent_interface = IContainer

    @property
    def title(self):
        result = II18n(self.context).queryAttribute('title', request=self.request)
        if not result:
            result = '{{ %s }}' % getName(self.context)
        return result

    @jsaction.handler(buttons['dialog_submit'])
    def submit_handler(self, event, selector):
        return '''$.ZBlog.form.edit(this.form);'''

    @jsaction.handler(buttons['dialog_cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZBlog.dialog.close();'

    @ajax.handler
    def ajaxEdit(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        changes = self.applyChanges(data)
        parent = getParent(self.context, self.parent_interface)
        if changes:
            notify(ObjectModifiedEvent(parent))
        return self.getOutput(writer, parent, changes)

    def getOutput(self, writer, parent, changes=()):
        status = changes and u'OK' or u'NONE'
        return writer.write({ 'output': status })


class PresentationNamespaceTraverser(namespace.view):
    """++presentation++ namespace"""

    def getSkin(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return None
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return None
        return queryUtility(IBrowserSkinType, skin_name)

    def traverse(self, name, ignored):
        skin = self.getSkin()
        if skin is None:
            raise TraversalError('++presentation++')
        fake = copy.copy(self.request)
        applySkin(fake, skin)
        adapter = queryMultiAdapter((self.context, fake), IPresentationTarget)
        if adapter is not None:
            try:
                return adapter.target_interface(self.context)
            except:
                pass
        raise TraversalError('++presentation++')


class BasePresentationEditForm(BaseDialogSimpleEditForm):
    """Presentation edit form"""

    implements(IPresentationForm)

    layout = getLayoutTemplate()

    def __init__(self, context, request):
        super(BasePresentationEditForm, self).__init__(context, request)
        skin = self.getSkin()
        if skin is None:
            raise NotFound(self.context, self.name, self.request)
        fake = copy.copy(self.request)
        applySkin(fake, skin)
        adapter = queryMultiAdapter((self.context, fake, self), IPresentationTarget)
        if adapter is None:
            adapter = queryMultiAdapter((self.context, fake), IPresentationTarget)
        if adapter is None:
            raise NotFound(self.context, self.name, self.request)
        self.interface = adapter.target_interface

    def getContent(self):
        return self.interface(self.context)

    @property
    def fields(self):
        return field.Fields(self.interface)

    def getSkin(self):
        skinnable = getParent(self.context, ISkinnable)
        if skinnable is None:
            return None
        skin_name = skinnable.getSkin()
        if skin_name is None:
            return None
        return queryUtility(IBrowserSkinType, skin_name)

    @ajax.handler
    def ajaxEdit(self):
        return super(BasePresentationEditForm, self).ajaxEdit(self)

    @ajax.handler
    def ajaxSearch(self):
        writer = getUtility(IJSONWriter)
        title = self.request.form.get('title')
        if not title:
            return writer.write(None)
        query = getUtility(IQuery)
        intids = getUtility(IIntIds)
        result = []
        for obj in query.searchResults(Text(('Catalog', 'title'),
                                            { 'query': title + '*',
                                              'ranking': True })):
            result.append({ 'oid': intids.register(obj),
                            'title': II18n(obj).queryAttribute('title') })
        return writer.write(result)


class BaseDialogEditForm(BaseDialogSimpleEditForm):
    """Base dialog edit form"""

    parent_view = None
    handle_upload = False

    @ajax.handler
    def ajaxEdit(self):
        # Update resource throught AJAX request
        # JSON results have to be included in a textarea to handle JQuery.Form plugin file uploads
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        changes = self.applyChanges(data)
        parent = getParent(self.context, self.parent_interface)
        if changes:
            notify(ObjectModifiedEvent(parent))
        return self.getOutput(writer, parent, changes)

    def getOutput(self, writer, parent, changes=()):
        if self.parent_view is not None:
            view = self.parent_view(parent, self.request)
            view.update()
            return '<textarea>%s</textarea>' % writer.write({ 'output': u"<!-- OK -->\n" + view.output() })
        else:
            status = changes and u'OK' or u'NONE'
            return writer.write({ 'output': status })


class BaseIndexView(TemplateBasedPage):
    """Base index view"""

    implements(IBaseIndexView)

    presentation = None

    def update(self):
        super(BaseIndexView, self).update()
        adapter = queryMultiAdapter((self.context, self.request, self), IPresentationTarget)
        if adapter is None:
            adapter = queryMultiAdapter((self.context, self.request), IPresentationTarget)
        if adapter is not None:
            interface = adapter.target_interface
            self.presentation = interface(self.context)


class SkinSelectWidget(SelectWidget):
    noValueMessage = _("(inherit parent skin)")

def SkinSelectWidgetFactory(field, request):
    return widget.FieldWidget(field, SkinSelectWidget(request))


@adapter(ISkinnable, IBeforeTraverseEvent)
def handleSkinTraversal(object, event):
    if IBrowserRequest.providedBy(event.request):
        path = event.request.get('PATH_INFO', '')
        if (path.find('++skin++') < 0):
            skin_name = ISkinnable(object).getSkin()
            if not skin_name:
                skin_name = 'ZBlog'
            skin = queryUtility(IBrowserSkinType, skin_name)
            if skin is not None:
                applySkin(event.request, skin)


@adapter(IText, IBaseForm, IZTFYBlogLayer)
@implementer(IHTMLWidgetSettings)
def  HTMLWidgetAdapterFactory(field, form, request):
    """Create widget adapter matching content's applied skin"""
    settings = None
    target = getParent(form.context, ISkinnable)
    if target is not None:
        skin_name = ISkinnable(target).getSkin()
        if not skin_name:
            skin_name = 'ZBlog'
        skin = queryUtility(IBrowserSkinType, skin_name)
        if skin is not None:
            fake = copy.copy(request)
            applySkin(fake, skin)
            settings = queryMultiAdapter((field, form, fake), IHTMLWidgetSettings)
    return settings


class HTMLWidgetAdapter(object):
    """HTML widget settings adapter"""

    adapts(IText, IBaseForm, IZTFYBlogFrontLayer)
    implements(IHTMLWidgetSettings)

    def __init__(self, field, form, request):
        self.field = field
        self.form = form
        self.request = request

    mce_invalid_elements = 'h1,h2'

    @property
    def mce_external_image_list_url(self):
        target = getParent(self.form.context, IResourceContainerTarget)
        if target is not None:
            return '%s/@@getImagesList.js' % absoluteURL(target, self.request)
        return None

    @property
    def mce_external_link_list_url(self):
        target = getParent(self.form.context, IResourceContainerTarget)
        if target is not None:
            return '%s/@@getLinksList.js' % absoluteURL(target, self.request)
        return None
