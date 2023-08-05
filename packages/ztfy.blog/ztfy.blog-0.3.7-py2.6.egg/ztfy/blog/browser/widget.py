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
from z3c.form.interfaces import IFieldWidget, ITextWidget
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IField

# import local interfaces
from ztfy.blog.layer import IZTFYBlogLayer

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter, getUtility
from zope.i18n import translate
from zope.interface import implementer, implementsOnly
from zope.schema import TextLine

# import local packages

from ztfy.blog import _


class IInternalReferenceWidget(ITextWidget):
    """Interface reference widget interface"""

    target_title = TextLine(title=_("Target title"),
                            readonly=True)


class InternalReferenceWidget(TextWidget):
    """Internal reference selection widget"""

    implementsOnly(IInternalReferenceWidget)

    @property
    def target_title(self):
        if not self.value:
            return u''
        value = self.request.locale.numbers.getFormatter('decimal').parse(self.value)
        intids = getUtility(IIntIds)
        target = intids.queryObject(value)
        return translate(_('%s (OID: %d)'), context=self.request) % (II18n(target).queryAttribute('title', request=self.request), value)

@adapter(IField, IZTFYBlogLayer)
@implementer(IFieldWidget)
def InternalReferenceFieldWidget(field, request):
    """IFieldWidget factory for InternalReferenceWidget"""
    return FieldWidget(field, InternalReferenceWidget(request))
