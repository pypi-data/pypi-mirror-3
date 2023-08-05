#############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

import grokcore.annotation.interfaces
import grokcore.component.interfaces
import grokcore.security.interfaces
import grokcore.site.interfaces
import grokcore.view.interfaces
import grokcore.viewlet.interfaces
import grokcore.formlib.interfaces


class IFiveGrokView(grokcore.view.interfaces.IGrokView):
    """A five.grok view is a specific implementation of a
    grokcore.view.View.
    """


class IFiveGrokAPI(grokcore.annotation.interfaces.IGrokcoreAnnotationAPI,
                   grokcore.component.interfaces.IGrokcoreComponentAPI,
                   grokcore.security.interfaces.IGrokcoreSecurityAPI,
                   grokcore.site.interfaces.IGrokcoreSiteAPI,
                   grokcore.view.interfaces.IGrokcoreViewAPI,
                   grokcore.viewlet.interfaces.IGrokcoreViewletAPI,
                   grokcore.formlib.interfaces.IGrokcoreFormlibAPI):
    """Official five.grok API.
    """
