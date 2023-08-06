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
from z3c.form.interfaces import ITextWidget, ISubForm, ITextAreaWidget
from zope.container.interfaces import IContainer

# import local interfaces

# import Zope3 packages
from z3c.form import button
from z3c.formjs import jsaction
from zope.interface import Interface
from zope.schema import Bool, TextLine, List, Choice, Object

# import local packages

from ztfy.skin import _


#
# Custom widgets interfaces
#

class IDateWidget(ITextWidget):
    """Marker interface for date widget"""


class IDatetimeWidget(ITextWidget):
    """Marker interface for datetime widget"""


class IFixedWidthTextAreaWidget(ITextAreaWidget):
    """Marker interface for fixed width text area widget"""


#
# Default views interfaces
#

class IDefaultView(Interface):
    """Interface used to get object's default view name"""

    viewname = TextLine(title=_("View name"),
                        description=_("Name of the default view for the adapter object and request"),
                        required=True,
                        default=u'@@index.html')

    def getAbsoluteURL():
        """Get full absolute URL of the default view"""


class IContainedDefaultView(IDefaultView):
    """Interface used to get object's default view name while displayed inside a container"""


class IContainerAddFormMenuTarget(Interface):
    """Marker interface for base add form menu item"""


class IPropertiesMenuTarget(Interface):
    """Marker interface for properties menus"""


#
# Containers interfaces
#

class IOrderedContainerOrder(Interface):
    """Ordered containers interface"""

    def updateOrder(order):
        """Reset items in given order"""

    def moveUp(key):
        """Move given item up"""

    def moveDown(key):
        """Move given item down"""

    def moveFirst(key):
        """Move given item to first position"""

    def moveLast(key):
        """Move given item to last position"""


class IOrderedContainer(IOrderedContainerOrder, IContainer):
    """Marker interface for ordered containers"""


class IContainerBaseView(Interface):
    """Marker interface for container base view"""


class IOrderedContainerBaseView(Interface):
    """Marker interface for ordered container based view"""


class IOrderedContainerSorterColumn(Interface):
    """Marker interface for container sorter column"""


#
# Custom forms interfaces
#

class IEditFormButtons(Interface):
    """Default edit form buttons"""

    submit = button.Button(title=_("Submit"))
    reset = jsaction.JSButton(title=_("Reset"))


class IDialogAddFormButtons(Interface):
    """Default dialog add form buttons"""

    add = jsaction.JSButton(title=_("Add"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class IDialogDisplayFormButtons(Interface):
    """Default dialog display form buttons"""

    dialog_close = jsaction.JSButton(title=_("Close"))


class IDialogEditFormButtons(Interface):
    """Default dialog edit form buttons"""

    dialog_submit = jsaction.JSButton(title=_("Submit"))
    dialog_cancel = jsaction.JSButton(title=_("Cancel"))


class IBaseForm(Interface):
    """Marker interface for any form"""


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

    autocomplete = Choice(title=_("Auto-complete"),
                          values=('on', 'off'),
                          default='on')

    def createSubForms():
        """Initialize sub-forms"""

    def createTabForms():
        """Initialize tab-forms"""

    def getForms():
        """Get full list of forms"""


class IDialog(Interface):
    """Base interface for AJAX dialogs"""


#
# Breadcrumb interfaces
#

class IBreadcrumbInfo(Interface):
    """Get custom breadcrumb info of a given context"""

    visible = Bool(title=_("Visible ?"),
                   required=True,
                   default=True)

    title = TextLine(title=_("Title"),
                     required=True)

    path = TextLine(title=_("Path"),
                    required=False)
