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
from z3c.form.interfaces import ITextWidget, ISubForm

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import Bool, TextLine, List, Object

# import local packages

from ztfy.skin import _


class IDateWidget(ITextWidget):
    """Marker interface for date widget"""


class IDatetimeWidget(ITextWidget):
    """Marker interface for datetime widget"""


class ICustomExtractSubForm(ISubForm):
    """SubForm interface with custom extract method"""

    def extract():
        """Extract data and errors from input request"""


class ICustomUpdateSubForm(ISubForm):
    """SubForm interface with custom update method"""

    def updateContent(object, data):
        """Update custom content with given data"""


class IForm(Interface):
    """Base form interface"""

    title = TextLine(title=_("Form title"))

    legend = TextLine(title=_("Form legend"),
                      required=False)

    subforms = List(title=_("Sub-forms"),
                    value_type=Object(schema=ISubForm),
                    required=False)

    def createSubForms():
        """Initialize sub-forms"""

    def createTabForms():
        """Initialize tab-forms"""

    def getForms():
        """Get full list of forms"""


class IDialog(Interface):
    """Base interface for AJAX dialogs"""


class IBreadcrumbInfo(Interface):
    """Get custom breadcrumb info of a given context"""

    visible = Bool(title=_("Visible ?"),
                   required=True,
                   default=True)

    title = TextLine(title=_("Title"),
                     required=True)

    path = TextLine(title=_("Path"),
                    required=False)
