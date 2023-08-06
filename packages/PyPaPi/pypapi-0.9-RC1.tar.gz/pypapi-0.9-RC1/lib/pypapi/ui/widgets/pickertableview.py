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
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from pypapi.ui.cute.interfaces import IModelView, IDataContext, IForm
import pypapi.ui.resources
from pypapi.app.forms import PyPaPiForm
from pypapi.ui.cute.delegate import Delegate
from pypapi.db.interfaces import IListStore


DEFAULT_ROW_HEIGHT = 24
SPACING = 4
VSPACING = 0

class PickerTableView(QtGui.QWidget):
    """
    Una TableView popolabile tramite un form-picker.
    """

    implements(IModelView)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._initLayout()
        self.enabled_default = None
        self.selection_path = ''
        self.selection_cols = None
        self.selection_filter_terms = {}
        self.diff_selection = False
        self.auto_search = False
        self.auto_info = False
        self.quick_insert = False
        self.text_edited = False
        self.info_form_name = None

    def _createTableView(self):
        table_view = QtGui.QTableView(self)
        table_view.verticalHeader().setDefaultSectionSize(DEFAULT_ROW_HEIGHT)
        delegate = Delegate(table_view)
        table_view.setItemDelegate(delegate)
        table_view.setSortingEnabled(True)
        table_view.installEventFilter(self)
        self.connect(table_view, QtCore.SIGNAL('doubleClicked(const QModelIndex)'), self.infoRow)
        return table_view

    def _initLayout(self):
        self.main_layout = QtGui.QHBoxLayout(self)
        self.main_layout.setSpacing(SPACING)
        self.main_layout.setMargin(0)
        self.main_layout.setObjectName("main_layout")

        self.button_layout = QtGui.QVBoxLayout()
        self.button_layout.setSpacing(VSPACING)
        self.button_layout.setObjectName("button_layout")

        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.button_layout.addItem(spacer)

        
        self.edit_quick_insert = QtGui.QLineEdit(self)
        self.edit_quick_insert.setFixedSize(30, 20)
        self.edit_quick_insert.hide()
        self.button_layout.addWidget(self.edit_quick_insert)
        self.connect(self.edit_quick_insert, QtCore.SIGNAL('textEdited ( const QString & )'), lambda s: self.setTextEdited(True))
        self.connect(self.edit_quick_insert, QtCore.SIGNAL('editingFinished ()'), self.quickEditingFinished)

        self.button_info = QtGui.QToolButton(self)
        self.button_info.setIcon(QtGui.QIcon(":/icons/information.png"))
        self.button_info.setObjectName("button_info")
        self.button_layout.addWidget(self.button_info)
        self.connect(self.button_info, QtCore.SIGNAL('clicked()'), self.infoRow)

        self.button_open = QtGui.QToolButton(self)
        self.button_open.setIcon(QtGui.QIcon(":/icons/open.png"))
        self.button_open.setObjectName("button_open")
        self.button_layout.addWidget(self.button_open)
        self.connect(self.button_open, QtCore.SIGNAL('clicked()'), self.openRow)

        self.button_add = QtGui.QToolButton(self)
        self.button_add.setIcon(QtGui.QIcon(":/icons/add.png"))
        self.button_add.setObjectName("button_add")
        self.button_layout.addWidget(self.button_add)
        self.connect(self.button_add, QtCore.SIGNAL('clicked()'), self.addRow)

        self.button_del = QtGui.QToolButton(self)
        self.button_del.setIcon(QtGui.QIcon(":/icons/delete.png"))
        self.button_del.setObjectName("button_del")
        self.button_layout.addWidget(self.button_del)
        self.connect(self.button_del, QtCore.SIGNAL('clicked()'), self.delRow)

        self.main_layout.addLayout(self.button_layout)

        self.table_layout = QtGui.QVBoxLayout()
        self.table_layout.setObjectName("table_layout")

        self.table_view = self._createTableView()
        self.table_view.setSelectionBehavior(QtGui.QTableView.SelectRows)
        # portarla come proprietà per il designer?
        self.table_view.setSelectionMode(QtGui.QTableView.ExtendedSelection)
        self.table_view.setDragEnabled(True)
        self.table_view.setAcceptDrops(True)
        self.table_view.setDropIndicatorShown(True)
        self.table_view.setDragDropMode(QtGui.QTableView.InternalMove)
        self.table_view.setObjectName("table_view")
        #self.table_view.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.table_view.setSortingEnabled(True)
        # popup menu
        self.popup_menu = QtGui.QMenu(self)
        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.table_view, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.contextMenu)
        self.action_resize_rows = QtGui.QAction("Ridimensiona al contenuto", self)
        self.popup_menu.addAction(self.action_resize_rows)
        self.action_collapse_rows = QtGui.QAction("Ridimensiona ad una riga", self)
        self.popup_menu.addAction(self.action_collapse_rows)

        self.table_layout.addWidget(self.table_view)
        self.main_layout.addLayout(self.table_layout)

    def eventFilter(self, qobject, qevent):
        if qevent.type() == QtCore.QEvent.KeyPress and qevent.key() == QtCore.Qt.Key_Return:
            self.openRow()
        return False

    def _getSelRows(self):

        return self.selection_model.selectedRows()

    sel_rows = property(_getSelRows)

    def setWordWrap(self, mode):
        self.table_view.setWordWrap(mode)

    def setSortingEnabled(self, mode):
        return self.table_view.setSortingEnabled(mode)

    def setQuickInsertEnabled(self, mode=True):
        #self.quick_insert.setEnabled(mode)
        if mode is True:
            self.edit_quick_insert.show()
        else:
            self.edit_quick_insert.hide()
        self.quick_insert = mode
    def getQuickInsertEnabled(self):
        return self.quick_insert
    quickInsertEnabled = QtCore.pyqtProperty('bool', getQuickInsertEnabled, setQuickInsertEnabled)

    def setInfoEnabled(self, mode=True):
        self.button_info.setEnabled(mode)
    def getInfoEnabled(self):
        return self.button_info.isEnabled()
    infoEnabled = QtCore.pyqtProperty('bool', getInfoEnabled, setInfoEnabled)

    def setOpenEnabled(self, mode=True):
        self.button_open.setEnabled(mode)
    def getOpenEnabled(self):
        return self.button_open.isEnabled()
    openEnabled = QtCore.pyqtProperty('bool', getOpenEnabled, setOpenEnabled)

    def setAddEnabled(self, mode=True):
        self.button_add.setEnabled(mode)
    def getAddEnabled(self):
        return self.button_add.isEnabled()
    addEnabled = QtCore.pyqtProperty('bool', getAddEnabled, setAddEnabled)

    def setDelEnabled(self, mode=True):
        self.button_del.setEnabled(mode)
    def getDelEnabled(self):
        return self.button_del.isEnabled()
    delEnabled = QtCore.pyqtProperty('bool', getDelEnabled, setDelEnabled)

    def setAutosearchEnabled(self, mode=True):
        self.auto_search = mode
    def getAutosearchEnabled(self):
        return self.auto_search
    autosearchEnabled = QtCore.pyqtProperty('bool', getAutosearchEnabled, setAutosearchEnabled)

    def setAutoinfoEnabled(self, mode=True):
        self.auto_info = mode
    def getAutoinfoEnabled(self):
        return self.auto_info
    autoinfoEnabled = QtCore.pyqtProperty('bool', getAutoinfoEnabled, setAutoinfoEnabled)

    def textEdited(self):
        return self._text_edited
    def setTextEdited(self, value):
        self._text_edited = value
    text_edited = property(textEdited, setTextEdited)

    def setModel(self, model):
        self.table_view.setModel(model)

    def model(self):
        return self.table_view.model()

    def setItemDelegate(self, delegate):
        self.table_view.setItemDelegate(delegate)

    def itemDelegate(self):
        return self.table_view.itemDelegate()

    def setSelectionModel(self, sel_model):

        self.selection_model = sel_model
        self.table_view.setSelectionModel(self.selection_model)

    def setEnabled(self, mode):
        if self.enabled_default is None:
            self.enabled_default = [b for b in ('Open', 'Add', 'Del', 'Info') if getattr(self, 'get%sEnabled' % b)() is True]
        for b in self.enabled_default:
            getattr(self, 'set%sEnabled' % b)(mode)
        if mode is True:
            self.table_view.setDragDropMode(QtGui.QTableView.InternalMove)
        else:
            self.table_view.setDragDropMode(QtGui.QTableView.NoDragDrop)

    def delRow(self):
        model = self.model()
        sel_rows = [sr.row() for sr in self.sel_rows]
        sel_rows.sort()
        while sel_rows:
            model.removeRows(sel_rows.pop(), 1)
        self.editPrimaryElement()

    def addRow(self, search_id=None):
        n_pre = self.model().rowCount()
        dc = IDataContext(self)
        if self.selection_path is '':
            dc.insertElement()
        else:
            if search_id is not None:
                dc.selectFromId(self.selection_path, search_id,
                                self.diff_selection, False, False,
                                self.selection_cols,
                                **self.selection_filter_terms)
            else:
                dc.selectFrom(self.selection_path, self.diff_selection, False,
                              False, self.selection_cols,
                              **self.selection_filter_terms)
        if self.model().rowCount() == n_pre:
            return
        self.editPrimaryElement()
        if self.auto_info is True:
            element = self.model().getEntityByRow(self.model().rowCount()-1)
            form = IForm(element)
            form.edit(0)
            if isinstance(form, QtGui.QDialog):
                form.first = True
                res = form.exec_()
                if res == QtGui.QDialog.Rejected:
                    self.table_view.selectRow(self.table_view.model().rowCount()-1)
                    self.delRow()
            else:
                form.show()

    def openRow(self):
        """"""
        self.infoRow(self.selection_path)

    def infoRow(self, selection=None):
        """Apro la view per l'elemento selezionato"""
        if self.infoEnabled is False and self.openEnabled is False:
            return
        if isinstance(selection, QtCore.QModelIndex):
            # dclick
            selection = None
        if len(self.sel_rows) == 1:
            index = self.sel_rows[0]
            model = self.model()
            element = model.store[index.row()]
            if selection is not None and selection != '':
                element = getattr(element, selection)
            if self.info_form_name is None:
                form = IForm(element)
            else:
                store = IListStore(element)
                form = getMultiAdapter((store, None), IForm, self.info_form_name)
            form.edit(0)
            form.show()
            self.editPrimaryElement()
        self.table_view.emit(QtCore.SIGNAL("referenceChanged(QString)"), "")

    def editPrimaryElement(self):
        parent = self.parent()
        while parent is not None and not isinstance(parent, PyPaPiForm):
            parent = parent.parent()
        if parent is not None:
            pdc = IDataContext(parent)
            pdc.editElement()

    def horizontalHeader(self):
        return self.table_view.horizontalHeader()

    def contextMenu(self, point):
         action = self.popup_menu.exec_(self.table_view.mapToGlobal(point))
         if action is self.action_resize_rows:
             self.resizeRows()
         elif action is self.action_collapse_rows:
             self.collapseRowsHeight()

    def resizeRows(self, all=False):
        sel_rows = [sr.row() for sr in self.selection_model.selectedRows()]
        if all is True or len(sel_rows) == 0:
            self.table_view.resizeRowsToContents()
        else:
            for row in sel_rows:
                self.table_view.resizeRowToContents(row)

    def collapseRowsHeight(self, all=False):
        if all is True:
            self.table_view.verticalHeader().setDefaultSectionSize(DEFAULT_ROW_HEIGHT)
            return
        sel_rows = [sr.row() for sr in self.selection_model.selectedRows()]
        for row in sel_rows:
            self.table_view.setRowHeight(row, DEFAULT_ROW_HEIGHT)

    def quickEditingFinished(self):
        if self.text_edited is True and len(self.edit_quick_insert.text())>0:
            self.find()
            self.edit_quick_insert.clear()
            self.edit_quick_insert.setFocus(QtCore.Qt.OtherFocusReason)

    def find(self):
        """
        Chiede al DataContext di occuparsi della selezione del (degli) item,
        e dell'iserimento nello store.
        """
        search_text = self.edit_quick_insert.text()
        try:
            search_id = int(search_text)
        except ValueError:
            search_id = None
        if search_id is not None:
            self.addRow(search_id)
