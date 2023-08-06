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
from zope.authentication.interfaces import IAuthentication

# import local interfaces
from ztfy.security.interfaces import IGrantedRoleEvent

# import Zope3 packages
from zope.component import adapter, getUtilitiesFor

# import local packages


@adapter(IGrantedRoleEvent)
def handleGrantedOperatorRole(event):
    if event.role in ('ztfy.BlogManager', 'ztfy.BlogContributor'):
        for _name, auth in getUtilitiesFor(IAuthentication):
            operators = auth.get('groups', {}).get('operators', None)
            if operators and (event.principal not in operators.principals):
                operators.principals = operators.principals + (event.principal,)
