##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import transaction
import zope.interface
import zope.i18nmessageid

from z3c.form import button
from z3c.formui import form
from z3c.table import table
from z3c.template.template import getPageTemplate

from z3c.tabular import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


# simple template rendering aware table base class
class TemplateTable(table.Table):
    """Template aware teble."""

    zope.interface.implements(interfaces.ITemplateTable)

    template = getPageTemplate()

    def render(self):
        """Render the template."""
        return self.template()


# simple form aware table base class
class TableBase(TemplateTable):
    """Generic table class with form action support used as form mixin base.

    This table base class allows you to mixin custom forms as base.
    """

    prefix = 'formTable'

    # internal defaults
    actions = None
    hasContent = False
    nextURL = None
    selectedItems = []
    ignoreContext = False

    # table defaults
    cssClasses = {'table': 'contents'}
    cssClassEven = u'even'
    cssClassOdd = u'odd'
    cssClassSelected = u'selected'

    batchSize = 25
    startBatchingAt = 25

    # customize this part
    allowCancel = True
    supportsCancel = False

    def update(self):
        # 1. setup widgets
        self.updateWidgets()
        # 2. setup search values, generate rows, setup headers and columns
        super(TableBase, self).update()
        # 3. setup conditions
        self.setupConditions()
        # 4. setup form part
        self.updateActions()
        if self.actions is not None:
            self.actions.execute()

    def setupConditions(self):
        self.hasContent = bool(self.rows)
        if self.allowCancel:
            self.supportsCancel = self.hasContent

    def updateAfterActionExecution(self):
        """Update table data if subform changes soemthing."""
        # first update table data which probably changed
        super(TableBase, self).update()
        # second setup conditions
        self.setupConditions()
        # third update action which we have probably different conditions for
        self.updateActions()

    @button.buttonAndHandler(_('Cancel'), name='cancel',
                             condition=lambda form:form.supportsCancel)
    def handleCancel(self, action):
        self.nextURL = self.request.getURL()

    def render(self):
        """Render the template."""
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return ""
        return self.template()


class FormTable(TableBase, form.Form):
    """Generic table class with form action support based on IForm."""

    zope.interface.implements(interfaces.IFormTable)

    template = getPageTemplate()


class DeleteFormTable(FormTable):
    """Table class with form action support based on IForm."""

    zope.interface.implements(interfaces.IDeleteFormTable)

    prefix = 'deleteFormTable'

    # internal defaults
    supportsCancel = False
    supportsDelete = False

    deleteErrorMessage = _('Could not delete the selected items')
    deleteNoItemsMessage = _('No items selected for delete')
    deleteSuccessMessage = _('Data successfully deleted')

    # customize this part
    allowCancel = True
    allowDelete = True

    def executeDelete(self, item):
        raise NotImplementedError('Subclass must implement executeDelete')

    def setupConditions(self):
        self.hasContent = bool(self.rows)
        if self.allowCancel:
            self.supportsCancel = self.hasContent
        if self.allowDelete:
            self.supportsDelete = self.hasContent

    def doDelete(self, action):
        if not len(self.selectedItems):
            self.status = self.deleteNoItemsMessage
            return
        try:
            for item in self.selectedItems:
                self.executeDelete(item)
            # update the table rows before we start with rendering
            self.updateAfterActionExecution()
            if self.status is None:
                # probably execute delete or updateAfterAction already set a
                # status
                self.status = self.deleteSuccessMessage
        except KeyError:
            self.status = self.deleteErrorMessage
            transaction.doom()

    @button.buttonAndHandler(_('Delete'), name='delete',
                             condition=lambda form:form.supportsDelete)
    def handleDelete(self, action):
        self.doDelete(action)


# form table including a sub form
class SubFormTable(DeleteFormTable):
    """Form table including a sub form based on IForm."""

    zope.interface.implements(interfaces.ISubFormTable)

    buttons = DeleteFormTable.buttons.copy()
    handlers = DeleteFormTable.handlers.copy()

    prefix = 'subFormTable'

    # internal defaults
    subForm = None
    supportsEdit = False

    # error messages
    subFormNoItemMessage = _('No item selected for edit')
    subFormToManyItemsMessage = _('Only one item could be selected for edit')
    subFormNotFoundMessage = _('No edit form found for selected item')

    # customize this part
    # use subFormClass or use subFormName. If you set both it will end in
    # using subFormClass. See updateSubForm for details.
    subFormClass = None
    subFormName = u''
    allowEdit = True

    def update(self):
        # 1. setup widgets
        super(SubFormTable, self).update()
        # 2. setup form after we set probably a selectedItem
        self.updateSubForm()

    def setupConditions(self):
        super(SubFormTable, self).setupConditions()
        if self.allowEdit:
            self.supportsEdit = self.hasContent

    @property
    def selectedItem(self):
        if len(self.selectedItems) == 0:
            return None
        if len(self.selectedItems) > 1:
            self.status = self.subFormToManyItemsMessage
            return None
        return self.selectedItems[0]

    def setUpSubForm(self, selectedItem):
        if self.subFormClass is not None:
            return self.subFormClass(selectedItem, self.request)
        elif self.subFormName is not None:
            return zope.component.queryMultiAdapter((selectedItem,
                self.request), name=self.subFormName)

    def updateSubForm(self):
        if not self.supportsEdit:
            return
        selectedItem = self.selectedItem
        if selectedItem is None:
            return
        # set table as parent
        self.subForm = self.setUpSubForm(selectedItem)
        if self.subForm is None:
            self.status = self.subFormNotFoundMessage
            return
        self.subForm.__parent__ = self
        # udpate edit form
        self.subForm.update()

    def doSubForm(self, action):
        if self.subForm is None:
            return
        # set ignore request and update again
        self.subForm.ignoreRequest = True
        self.subForm.update()

    @button.buttonAndHandler(u'Edit', condition=lambda form:form.supportsEdit)
    def handleSubForm(self, action):
        self.updateSubForm()
        self.doSubForm(action)

    @button.buttonAndHandler(_('Cancel'), name='cancel',
                             condition=lambda form:form.supportsCancel)
    def handleCancel(self, action):
        self.nextURL = self.request.getURL()
