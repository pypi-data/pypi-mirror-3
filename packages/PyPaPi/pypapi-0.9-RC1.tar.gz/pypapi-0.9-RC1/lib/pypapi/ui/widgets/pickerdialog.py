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


from PyQt4 import QtCore, QtGui
from datetime import date, timedelta
import zope.interface
from zope import schema
from zope.component import adapter, provideAdapter, getUtility
from zope.component.registry import Components
import pypapi.ui.resources
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.storage import SingleItemStore
from pypapi.db.field import DbObject
from pypapi.db.interfaces import IRelationResolver
from pypapi.ui.cute.interfaces import ISelectForm, ISelectFormLite, IPickerEntityWidget, \
     IDataContext, IColumn, IModel
from pypapi.ui.cute.form import BaseForm, StoreEditForm
from pypapi.ui.cute.search import CriteriaDialog
from pypapi.ui.cute.model import TableModel
from pypapi.ui.cute.delegate import Delegate
from pypapi.ui.widgets.pickerentity import PickerEntity


class PickerDialog(QtGui.QDialog, StoreEditForm):
    """
    QDialog per la selezione degli elementi da aggiungere alla TableView
    """

    zope.interface.implements(ISelectForm)

    def __init__(self, allow_multi=True, selection_filter_func=None, source=None, interface=None, **kw):
        QtGui.QDialog.__init__(self, None)
        self._postInit(allow_multi, selection_filter_func, source, interface, **kw)

    def _postInit(self, allow_multi, selection_filter_func, source, interface, **kw):
        if len(kw)>0:
            store = list(source)
            StoreEditForm.__init__(self, store, **kw)
        self._parent = None
        self._limit = None
        self._quick = None
        self._initLayout()
        self.selection = []
        self.root_interface = interface
        if selection_filter_func is None:
            self.selection_filter_func = lambda s: s
        else:
            self.selection_filter_func=selection_filter_func
        if allow_multi is True:
            self.table_view.setSelectionMode(self.table_view.MultiSelection)
        else:
            self.table_view.setSelectionMode(self.table_view.ExtendedSelection)
        delegate = Delegate(self.table_view)
        self.table_view.setItemDelegate(delegate)
        if source is not None:
            criteria = CriteriaDialog(source)
            self.criteria = criteria
            if len(self.criteria.search_wdgs) > 0:
                layout = self.layout()
                layout.addWidget(criteria)
                self.button_search = QtGui.QToolButton(self)
                self.button_search.setIcon(QtGui.QIcon(":/icons/key.png"))
                self.button_search.setObjectName("button_find")
                self.button_search.setShortcut(QtGui.QKeySequence.Find)
                self.connect(self.button_search, QtCore.SIGNAL('clicked()'), self.executeSearch)
                criteria.grid.addWidget(self.button_search, criteria.grid.rowCount(), 1, QtCore.Qt.AlignRight)
            try:
                criteria.grid.itemAtPosition(0, 1).widget().setFocus(QtCore.Qt.OtherFocusReason)
            except AttributeError:
                pass

    def eventFilter(self, qobject, qevent):
        if qevent.type() == QtCore.QEvent.KeyPress and qevent.key() == QtCore.Qt.Key_Return:
            if len(self.selection)>0:
                self.accept()
        return False

    def setQuickInsertForm(self, form):
        self._quick = form
        self.button_add =  QtGui.QToolButton(self)
        self.button_add.setIcon(QtGui.QIcon(":/icons/add.png"))
        self.button_add.setObjectName("button_add")
        self.button_add.setShortcut(QtGui.QKeySequence.New)
        self.criteria.grid.addWidget(self.button_add, self.criteria.grid.rowCount(), 1, QtCore.Qt.AlignRight)
        self.connect(self.button_add, QtCore.SIGNAL('clicked()'), self.executeQuickInsert)
        self.button_add.setEnabled(False)
    def getQuickInsertForm(self):
        return self._quick
    quickInsertForm = property(getQuickInsertForm, setQuickInsertForm)

    def loadUi(self):
        pass

    # XXX: La Dialog non viene 'parentata' in senso stretto QT, ma mi serve
    #        che 'parent()' restituisca la window di apertura (objectDataContext)
    def setParent(self, parent):
        self._parent = parent
    def parent(self):
        return self._parent

    def _setParentForm(self, form):
        self._parent_form = form
        self.setParent(form)
    def _getParentForm(self):
        return self._parent_form
    parent_form = property(_getParentForm, _setParentForm)

    def setLimit(self, limit):
        self._limit = limit

    def _initLayout(self):
        self.setWindowTitle('Ricerca e selezione')
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setObjectName("layout")
        self.table_view = QtGui.QTableView()
        self.table_view.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.table_view.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.table_view.setMinimumHeight(150)
        self.table_view.setSortingEnabled(True)
        self.table_view.installEventFilter(self)
        self.connect(self.table_view, QtCore.SIGNAL('keyPressEvent(QKeyEvent)'), self.accept)
        layout.addWidget(self.table_view, 1)
        self.filter_entry = QtGui.QLineEdit()
        self.connect(self.filter_entry, QtCore.SIGNAL('textChanged(QString)'), self.applyFilter)
        filter_label = QtGui.QLabel()
        filter_label.setPixmap(QtGui.QPixmap(":/icons/find.png"))
        self.search_log = QtGui.QLabel()
        button_accept = QtGui.QToolButton(self)
        button_accept.setIcon(QtGui.QIcon(":/icons/accept.png"))
        button_accept.setObjectName("button_accept")
        button_cancel =  QtGui.QToolButton(self)
        button_cancel.setIcon(QtGui.QIcon(":/icons/cancel.png"))
        button_cancel.setObjectName("button_add")
        button_layout = QtGui.QHBoxLayout()
        button_layout.setSpacing(4)
        button_layout.setObjectName("button_layout")
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        button_layout.addWidget(self.filter_entry)
        button_layout.addWidget(filter_label)
        button_layout.addWidget(self.search_log)
        button_layout.addItem(spacer)
        button_layout.addWidget(button_cancel)
        button_layout.addWidget(button_accept)
        layout.addLayout(button_layout)
        self.connect(button_cancel, QtCore.SIGNAL('clicked()'), self, QtCore.SLOT('close()'))
        self.connect(button_accept, QtCore.SIGNAL('clicked()'), self, QtCore.SLOT('accept()'))
        self.connect(self.table_view, QtCore.SIGNAL('doubleClicked(const QModelIndex)'), self,
                                             QtCore.SLOT('accept()'))
        self.resize(500, 300)


    def executeSearch(self, sorting=True):
        self.setSearchLog('Ricerca...')
        source = self.criteria.executeSearch()
        if source is None:
            self.search_log.setText('')
            return
        store = list(source)
        if self._limit is not None and len(store) >= self._limit:
            msg = "Presenti troppi elementi corrispondenti ai criteri di ricerca:\n"
            msg += "verranno presentati solo i primi %d." % self._limit
            confirm = QtGui.QMessageBox.information(None, 'Ricerca numerosa', msg, QtGui.QMessageBox.Yes)
            n = self._limit
        else:
            n = len(store)
        colnames = ('caption',)
        columns = [IColumn(self.root_interface.get(name)) for name in colnames]
        model = TableModel(store, columns=columns)
        model.editable = False
        self.setModel(model)
        if hasattr(self, 'button_search') and len(self.criteria.search_wdgs) == 0:
            self.button_search.setEnabled(False)
            self.button_search.setShortcut(QtGui.QKeySequence.Find)
        if sorting is True:
            self.table_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.table_view.selectRow(0)
        self.table_view.setFocus(QtCore.Qt.OtherFocusReason)
        if hasattr(self, 'button_add'):
            self.button_add.setEnabled(True)
        self._source = source
        self.setSearchLog('%d elementi trovati' % n)
        self.selection = []
        self.table_view.clearSelection()
        if n == 1:
            # select if only one element
            i = self.table_view.model().index(0, 0)
            self.table_view.selectionModel().select(i,  QtGui.QItemSelectionModel.Select)


    def setSearchLog(self, s):
        self.search_log.setText(s)

    def executeQuickInsert(self):
        """
        Esegue le dialog di inserimento veloce, e restituisce l'elemento creato
        """
        res = self.quickInsertForm.exec_()
        if res == self.quickInsertForm.Accepted:
            self.selection = self.selection_filter_func([self.quickInsertForm.entity,])
            self.accept()


    def setModel(self, model):
        self.table_view.setModel(model)
        self.selection_model = QtGui.QItemSelectionModel(model)
        self.table_view.setSelectionModel(self.selection_model)
        self.connect(self.selection_model, QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.selectRow)
        self.table_view.horizontalHeader().setStretchLastSection(True)

    def applyFilter(self, text=None):
        """
        Applica al superset il filtro descritto nella lineedit
        """
        if text is None:
            text = self.filter_entry.text()
        model = self.table_view.model()
        if text and model is not None:
            for i in range(model.rowCount()):
                if str(text).upper() in model.get(i, 0).get().upper():
                    self.table_view.setRowHidden(i, False)
                else:
                    self.table_view.setRowHidden(i, True)

    def selectRow(self, selected, deselected):
        model = self.table_view.model()
        for i in selected.indexes():
            self.selection.append(model.getEntityByRow(i.row()))
        for i in deselected.indexes():
            try:
                self.selection.remove(model.getEntityByRow(i.row()))
            except ValueError:
                # item not in list, no problem
                pass

    def accept(self):
        self.selection = self.selection_filter_func(self.selection)
        if hasattr(self, 'form'):
            self.form.store = list(self.selection)
            self.form.edit(0)
        QtGui.QDialog.accept(self)


class PickerDialogLite(PickerDialog):
    """
    Un QDialog più leggero (per il PickerEntity 'lite')
    """

    zope.interface.implements(ISelectFormLite)

    def __init__(self, allow_multi=True, selection_filter_func=None, source=None, interface=None, **kw):
        flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog
        QtGui.QDialog.__init__(self, None, flags)
        self.null_item = False
        self._entity_to_select = None
        self._postInit(allow_multi, selection_filter_func, source, interface, **kw)

    def _initLayout(self):
        self.setWindowTitle('Ricerca e selezione')
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName("layout")
        self.table_view = QtGui.QTableView()
        self.table_view.horizontalHeader().hide()
        self.table_view.verticalHeader().hide()
        self.table_view.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.table_view.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.table_view.setMinimumHeight(150)
        self.table_view.setSortingEnabled(False)
        self.table_view.installEventFilter(self)
        self.connect(self.table_view, QtCore.SIGNAL('keyPressEvent(QKeyEvent)'), self.accept)
        layout.addWidget(self.table_view, 1)
        self.connect(self.table_view, QtCore.SIGNAL('doubleClicked(const QModelIndex)'), self,
                                             QtCore.SLOT('accept()'))
        self.connect(self.table_view, QtCore.SIGNAL('clicked(const QModelIndex)'), self,
                                             QtCore.SLOT('accept()'))

    def setSearchLog(self, s):
        pass

    def eventFilter(self, qobject, qevent):
        accept = False
        if qevent.type() == QtCore.QEvent.MouseButtonPress and qevent.key() == QtCore.Qt.LeftButton:
            action = True
        elif qevent.type() == QtCore.QEvent.KeyPress and qevent.key() == QtCore.Qt.Key_Return:
            accept = True
        if accept is True:
            if len(self.selection)>0:
                self.accept()
        return False

    def setEntityToSelect(self, entity):
        self._entity_to_select = entity

    def setNullItem(self, mode):
        self.null_item = mode

    def executeSearch(self):
        PickerDialog.executeSearch(self, sorting=True)
        store = self.table_view.model().store
        # aggiungo il record NULL
        if self.null_item is True:
            store.insert(0, None)
        if self._entity_to_select is not None:
            try:
                idx = store.index(self._entity_to_select)
            except ValueError:
                idx = 0
            self.table_view.selectRow(idx)

