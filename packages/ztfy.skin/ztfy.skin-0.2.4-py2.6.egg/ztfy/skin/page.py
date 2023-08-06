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
from z3c.template.interfaces import ILayoutTemplate, IPageTemplate

# import local interfaces

# import Zope3 packages
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserPage

# import local packages


class BaseTemplateBasedPage(BrowserPage):

    template = None

    def update(self):
        pass

    def render(self):
        if self.template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()

    def __call__(self):
        self.update()
        return self.render()


class TemplateBasedPage(BaseTemplateBasedPage):

    layout = None

    def __call__(self):
        self.update()
        if self.layout is None:
            layout = getMultiAdapter((self, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()
