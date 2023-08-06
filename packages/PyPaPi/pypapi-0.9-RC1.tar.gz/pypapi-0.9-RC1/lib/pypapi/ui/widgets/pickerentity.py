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
from zope.component import provideHandler, adapter

from pypapi.ui.cute import interfaces, widget
import pypapi.ui.resources


class PickerEntity(QtGui.QWidget):
    """
    Una label con un pulsante di ricerca dell'entità
    da correlare 1-1
    """

    implements(interfaces.IPickerEntityWidget)

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.lineedit = QtGui.QLineEdit(self)
        self.lineedit.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed))
        self.connect(self.lineedit, QtCore.SIGNAL('editingFinished ()'), self.editingFinished)
        self.connect(self.lineedit, QtCore.SIGNAL('textEdited ( const QString & )'), lambda s: self.setTextEdited(True))
        self.button_find = QtGui.QToolButton(self)
        self.button_find.setIcon(QtGui.QIcon(":/icons/find.png"))
        self.button_find.setObjectName("button_find")
        self.connect(self.button_find, QtCore.SIGNAL('clicked()'), self.find)
        self.button_open = QtGui.QToolButton(self)
        self.button_open.setIcon(QtGui.QIcon(":/icons/open.png"))
        self.button_open.setObjectName("button_open")
        self.connect(self.button_open, QtCore.SIGNAL('clicked()'), self.open)
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.lineedit, 1)
        layout.addWidget(self.button_find, 2)
        layout.addWidget(self.button_open, 3)
        self.setFocusPolicy(QtCore.Qt.TabFocus)
        self.setLayout(layout)
        self.selection_path = ''
        self.selection_cols = None
        self.selection_filter_terms = {}
        self.diff_selection = False
        self.text_edited = False
        self.auto_search = False
        self.openEnabled = False
        self.liteModeEnabled = False
        self.null_item = False
        self.nullElementEnabled = False

    def mousePressEvent(self, e):
        if self.liteModeEnabled is True:
            return self.find()

    def setAutosearchEnabled(self, mode=True):
        self.auto_search = mode
    def getAutosearchEnabled(self):
        return self.auto_search
    autosearchEnabled = QtCore.pyqtProperty('bool', getAutosearchEnabled, setAutosearchEnabled)

    def setOpenEnabled(self, mode=True):
        if mode is True:
            self.button_open.show()
        else:
            self.button_open.hide()
        self.open_enabled = mode
    def getOpenEnabled(self):
        return self.open_enabled
    openEnabled = QtCore.pyqtProperty('bool', getOpenEnabled, setOpenEnabled)

    def setLiteModeEnabled(self, mode=True):
        self.lineedit.setEnabled(not mode)
        if mode is True:
            self.button_find.setIcon(QtGui.QIcon(":/icons/blue_arrow_down.png"))
        else:
            self.button_find.setIcon(QtGui.QIcon(":/icons/find.png"))
        self.litemode_enabled = mode
    def getLiteModeEnabled(self):
        return self.litemode_enabled
    liteModeEnabled = QtCore.pyqtProperty('bool', getLiteModeEnabled, setLiteModeEnabled)

    def setNullItemEnabled(self, mode=True):
        self.null_item = mode
    def getNullItemEnabled(self):
        return self.null_item
    nullItemEnabled = QtCore.pyqtProperty('bool', getNullItemEnabled, setNullItemEnabled)

    def text(self):

        return self.lineedit.text()

    def setText(self, value):

        if not isinstance(value, QtCore.QString):
            value = QtCore.QString(value)
        self.lineedit.setText(value)
        self.lineedit.setCursorPosition(0)
        self.button_open.setEnabled(value.length()>0)

    text = QtCore.pyqtProperty('QString', text, setText)


    def textEdited(self):

        return self._text_edited

    def setTextEdited(self, value):

        self._text_edited = value

    text_edited = property(textEdited, setTextEdited)


    def editingFinished(self):
        if self.text_edited is True:
            self.find()


    def find(self):
        """
        Chiede al DataContext di occuparsi della selezione del (degli) item,
        e dell'iserimento nello store.
        """
        search_text = self.lineedit.text()
        try:
            search_id = int(search_text)
        except ValueError:
            search_id = None
        dc = interfaces.IDataContext(self)
        if self.liteModeEnabled is True:
            rect = self.geometry()
            pos = self.mapToGlobal(QtCore.QPoint(0, 0))
            h = 100
            d_y = rect.height()
            new_rect = QtCore.QRect(pos.x(), pos.y() + d_y, rect.width(), h)
            lite = new_rect
        else:
            lite = False
        if search_id is not None and hasattr(dc, 'selectFrom'):
            selection = dc.selectFromId(self.selection_path, search_id,
                                        self.diff_selection, lite, self.nullItemEnabled,
                                        self.selection_cols, **self.selection_filter_terms)
        else:
            selection = dc.selectFrom(self.selection_path, self.diff_selection,
                                      lite, self.nullItemEnabled, self.selection_cols,
                                      **self.selection_filter_terms)
        if selection not in (None, []):
            item = selection[0]
            col_index = widget.resolveColumn(self, dc)[0]
            self.text = dc.model.getByEntity(item, dc.model.columns[col_index]).get()
        self.text_edited = False


    def open(self):
        """
        Apre la finestra delegata alla gestione dell'entità
        """
        entity = interfaces.IDataContext(self).current_entity
        form = interfaces.IForm(entity)
        form.edit(0)
        form.show()


@adapter(interfaces.IPickerEntityWidget, interfaces.IWidgetCreationEvent)
def pickerWidgetBinding(data_widget, event):

    dc = interfaces.IDataContext(data_widget)
    col_index = widget.resolveColumn(data_widget, dc)[0]
    dc.mapper.addMapping(data_widget, col_index, 'text')

provideHandler(pickerWidgetBinding)
