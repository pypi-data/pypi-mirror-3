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
from z3c.form.interfaces import ISubForm, IHandlerForm, DISPLAY_MODE

# import local interfaces
from ztfy.skin.interfaces import IForm, IDialog, ICustomUpdateSubForm

# import Zope3 packages
from z3c.form import subform, button
from z3c.formjs import ajax
from z3c.formui import form
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements
from zope.lifecycleevent import Attributes, ObjectCreatedEvent, ObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.jqueryui.browser import jquery_tools, jquery_progressbar

from ztfy.skin import _


class AjaxForm(ajax.AJAXRequestHandler):
    """Custom base form class used to handle AJAX errors
    
    This base class may be combined with other form based classes (form.AddForm or form.EditForm)
    which provide standard form methods
    """

    def getAjaxErrors(self):
        errors = {}
        errors['status'] = translate(self.status, context=self.request)
        for error in self.errors:
            error.update()
            error = removeSecurityProxy(error)
            if hasattr(error, 'widget'):
                widget = removeSecurityProxy(error.widget)
                errors.setdefault('errors', []).append({ 'id': widget.id,
                                                         'widget': translate(widget.label, context=self.request),
                                                         'message': translate(error.message, context=self.request) })
            else:
                errors.setdefault('errors', []).append({ 'message': translate(error.message, context=self.request) })
        return { 'output': u'ERRORS',
                 'errors': errors }


class AddForm(form.AddForm):
    """Custom AddForm
    
    This form overrides creation process to allow created contents to be
    'parented' before changes to be applied. This is required for ExtFile
    properties to work correctly.
    """

    implements(IForm)

    formErrorsMessage = _('There were some errors.')

    # override button to get translated label
    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def update(self):
        jquery_progressbar.need()
        super(AddForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result

    def createAndAdd(self, data):
        object = self.create(data)
        notify(ObjectCreatedEvent(object))
        self.add(object)
        self.updateContent(object, data)
        return object

    def updateContent(self, object, data):
        form.applyChanges(self, object, data)
        self.getForms()
        for subform in self.subforms:
            if ICustomUpdateSubForm.providedBy(subform):
                ICustomUpdateSubForm(subform).updateContent(object, data)
            else:
                form.applyChanges(subform, object, data)
        for tabform in self.tabforms:
            if ICustomUpdateSubForm.providedBy(tabform):
                ICustomUpdateSubForm(tabform).updateContent(object, data)
            else:
                form.applyChanges(tabform, object, data)


class DialogAddForm(AddForm):
    """Custom AJAX add form dialog"""

    implements(IDialog)


class EditForm(form.EditForm):
    """Custom EditForm"""

    implements(IForm)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def update(self):
        jquery_progressbar.need()
        super(EditForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    def applyChanges(self, data):
        content = self.getContent()
        changes = self.updateContent(content, data)
        # ``changes`` is a dictionary; if empty, there were no changes
        if changes:
            # Construct change-descriptions for the object-modified event
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(Attributes(interface, *names))
            # Send out a detailed object-modified event
            notify(ObjectModifiedEvent(content, *descriptions))
        return changes

    def updateContent(self, content, data):
        changes = form.applyChanges(self, content, data)
        self.getForms()
        for subform in self.subforms:
            if ICustomUpdateSubForm.providedBy(subform):
                ICustomUpdateSubForm(subform).updateContent(content, data)
            else:
                changes.update(form.applyChanges(subform, content, data))
        for tabform in self.tabforms:
            if ICustomUpdateSubForm.providedBy(tabform):
                ICustomUpdateSubForm(tabform).updateContent(content, data)
            else:
                changes.update(form.applyChanges(tabform, content, data))
        return changes

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result


class DialogEditForm(EditForm):
    """Custom AJAX edit dialog base class"""

    implements(IDialog)


class EditSubForm(subform.EditSubForm):
    """Custom EditSubForm
    
    Actually no custom code..."""

    tabLabel = None


class DisplayForm(form.DisplayForm):
    """Custom DisplayForm"""

    implements(IForm)

    cssClass = 'display-form'

    def update(self):
        super(DisplayForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(DisplayForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result


class DisplaySubForm(form.DisplayForm):
    """Custom display sub-form"""

    implements(IForm, ISubForm, IHandlerForm)

    cssClass = 'display-form'

    tabLabel = None
    mode = DISPLAY_MODE

    def __init__(self, context, request, parentForm):
        self.context = context
        self.request = request
        self.parentForm = self.__parent__ = parentForm


class DialogDisplayForm(DisplayForm):
    """Custom AJAX display dialog base class"""
