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
from pypapi.ui.cute.interfaces import ILookupDataWidget

class LineEditCombo(QtGui.QWidget):
    """
    Una combinazione tra un LineEdit e un ComboBox:
    il modello associato deve avere almeno due colonne.
    """

    implements(ILookupDataWidget)

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)

        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setFixedWidth(40)
        self.lineEdit.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding))
        #self.lineEdit.installEventFilter(self)

        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.comboBox.installEventFilter(self)

        self.list_idx = []

        #self.connect(self.lineEdit, SIGNAL('editingFinished()'), self._checkLineEdit)
        #self.connect(self.comboBox, SIGNAL('currentIndexChanged(int)'), self._checkComboBox)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.lineEdit, 0)
        layout.addWidget(self.comboBox, 1)
        self.setLayout(layout)

        self.resize(26, 200)

    def eventFilter(self, qobject, qevent):
        # piccolo hack per far andare il delegato, che non riceve
        # eventi di FocusOut perché questo widget nella sua totalità,
        # non può essere focalizzato. Del resto non lo si vuole,
        # altrimenti l'utente dovrebbe premere un'altra volta il tab
        # per uscire. Quindi, ad ogni evento FocusOut ricevuto dai
        # child sotto controllo (su cui è stato eseguito
        # installEventFilter(self), emetto un evento di pressione del
        # tasto enter e lo invio a me stesso, in modo che il delegato
        # che osserva, operi in modo appropriato
        if qevent.type() == QtCore.QEvent.FocusOut:
            app = QtGui.QApplication.instance()
            kevent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier)
            app.postEvent(self, kevent)
        return False

    def focusOutEvent(self, focus_event):
        return False

    def currentIndex(self):
        return self.comboBox.currentIndex()

    def setCurrentIndex(self, i):
        self.comboBox.setCurrentIndex(i)

    def resetCurrentIndex(self):
        self.comboBox.setCurrentIndex(-1)

    currentIndex = QtCore.pyqtProperty('int', currentIndex, setCurrentIndex, resetCurrentIndex)

    def model(self):
        return self.comboBox.model()

    def setModel(self, model):
        return self.comboBox.setModel(model)

    def modelColumn(self):
        return self.comboBox.modelColumn()

    def setModelColumn(self, column):
        return self.comboBox.setModelColumn(column)

#     def _checkLineEdit(self):
#         """
#         Seleziona in comboBox il lookup relativo alla chiave inserita in lineEdit
#         """
#         key = self.lineEdit.text()
#         try:
#             idx = self.list_idx.index(key)
#             self.comboBox.setCurrentIndex(idx)
#         except ValueError:
#             self.lineEdit.setText(u'')

#     def _checkComboBox(self, i):
#         """
#         Scrive nel LineEdit il valore della chiave primaria, andando a leggerlo
#         nella seconda colonna del modello di Lookup.
#         """
#         model = self.comboBox.model()
#         column = model.columns[1]
#         key = model.getByColumn(i, column).getDisplay().toString()
#         self.lineEdit.setText(key)


