# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@pypapi.org>
# and Municipality of Riva del Garda TN (Italy).
#
# This file is part of PyPaPi Framework.
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#


from PyQt4 import QtGui, QtCore
from zope.interface import implements
from pypapi.ui.cute.interfaces import ITreeModelView, IDataContext, IForm
from pypapi.ui.widgets.pickertableview import PickerTableView

class PickerTreeView(PickerTableView):
    """
    Una TableView popolabile tramite un form-picker.
    """

    implements(ITreeModelView)

    def __init__(self, parent=None):
        PickerTableView.__init__(self, parent)
        self._parent_attribute = ''
        self._child_attribute = ''

    def _createTableView(self):
        tree_view = QtGui.QTreeView(self)
        return tree_view

    def horizontalHeader(self):
        return None

    def setChildAttribute(self, attribute=''):
        self._child_attribute = attribute
    def getChildAttribute(self):
        return self._child_attribute
    childAttribute = QtCore.pyqtProperty('QString', getChildAttribute, setChildAttribute)

    def setParentAttribute(self, attribute=''):
        self._parent_attribute = attribute
    def getParentAttribute(self):
        return self._parent_attribute
    parentAttribute = QtCore.pyqtProperty('QString', getParentAttribute, setParentAttribute)

    def addRow(self):
        if len(self.sel_rows) == 0:
            parent = QtCore.QModelIndex()
        elif len(self.sel_rows) == 1:
            parent = self.sel_rows[0]
        else:
            msg = "E' necessario selezionare al massimo un elemento a cui allegarne uno nuovo."
            QtGui.QMessageBox.warning(None, 'Errore inserimento', msg, QtGui.QMessageBox.Ok)
            return
        dc = IDataContext(self)
        dc.selectFrom(self.selection_path, self.diff_selection, self.selection_cols, parent,
                      **self.selection_filter_terms)

    def infoRow(self, selection=None):

        if len(self.sel_rows) == 1:
            index = self.sel_rows[0]
            model = self.model()
            element = index.internalPointer().itemEntity
            if selection is not None:
                element = getattr(element, selection)
            form = IForm(element)
            form.edit(0)
            form.show()
        self.table_view.emit(QtCore.SIGNAL("referenceChanged(QString)"), "")
