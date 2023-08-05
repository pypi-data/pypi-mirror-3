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


import os, sys
from code import InteractiveInterpreter
from PyQt4 import QtGui, QtCore

PROMPT = '>>> '
MORE = '... '

#err = lambda s: sys.stderr.write(str(s))

class ConsoleForm(QtGui.QDialog):
    def __init__(self, parent=None,locals = None):
        QtGui.QDialog.__init__(self,parent)
        if locals is None:
            locals = locals()
        self.resize(600,400)
        verticalLayout = QtGui.QVBoxLayout()
        app = QtGui.QApplication.instance()
        self.pyconsole = Console(app = app, locals = locals, parent = self)
        verticalLayout.addWidget(self.pyconsole)
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonClose = QtGui.QPushButton("Close")
        self.buttonInfo = QtGui.QPushButton("Info")
        buttonBox.addButton(self.buttonInfo, QtGui.QDialogButtonBox.HelpRole)
        buttonBox.addButton(self.buttonClose, QtGui.QDialogButtonBox.RejectRole)
        verticalLayout.addWidget(buttonBox)
        self.connect(self.buttonInfo, QtCore.SIGNAL("clicked()"), self.about)
        self.connect(self.buttonClose, QtCore.SIGNAL("clicked()"), self.reject)
        self.setLayout(verticalLayout)
        self.setWindowTitle("Python Console")

    def about(self):
        "Mostra delle informazioni sull'applicazione"
        from pypapi import __doc__, __version__
        QtGui.QMessageBox.about(self, "Informazioni su PyPaPi, versione %s" % __version__,
                                __doc__)

    def abort(self):
        "Chiudi il dialog, senza effettuare l'autenticazione"
        self.reject()

class Console(QtGui.QTextEdit):
    def __init__(self, app = None, locals=None, parent=None):
        QtGui.QTextEdit.__init__(self, parent)

        self.app = app
        #locals.exit = self.exitconsole
        self.interpreter = InteractiveInterpreter(locals)

        sys.stdout = self
        sys.stderr = self
        sys.stdin = self

        self.line = QtCore.QString()
        self.lines = []
        self._history = []
        self._history_point = 0
        self.point = 0
        self.reading = False

        font = QtGui.QFont("Courier New", 12)
        font.setFixedPitch(1)
        self.setFont(font)

        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base,bgc)
        textc = QtGui.QColor(8,175,0)
        pal.setColor(QtGui.QPalette.Text,textc)
        self.setPalette(pal)
        self.insertPlainText(PROMPT)

    def flush(self):
        pass

    def isatty(self):
        return True

    def readline(self):
        self.reading = True
        self.__clearLine()
        self.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        while self.reading is True:
            self.app.processoneEvent()
        if self.line.length() == 0:
            return '\n'
        else:
            return str(self.line) 

    def write(self, text):
        self.insertPlainText(text)
        self.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)

    def __clearLine(self):
        self.line.truncate(0)
        self.point = 0

        #move cursor at the end
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)

    def __insertText(self, text):
        self.insertPlainText(text)
        self.line.insert(self.point, text)
        self.point += text.length()

    def __run(self):
        self.pointer = 0
        self.lines.append(str(self.line))
        if self.line.length()>0:
            self._history.append(str(self.line))
            self._history_point = 0
        source = '\n'.join(self.lines)
        res = self.interpreter.runsource(source)
        if res is True:
            self.insertPlainText(MORE)
        else:
            self.insertPlainText(PROMPT)
            self.lines = []
        self.__clearLine()

    def keyPressEvent(self, e):
        cur = self.textCursor()
        text = e.text()
        key = e.key()

        if text.length() > 0 and key >= 32 and key < 255:
            self.__insertText(text)
            return

        if key in (QtCore.Qt.Key_Shift, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Control):
            e.ignore()
            return

        if key == QtCore.Qt.Key_Backspace:
            if self.point:
                cur.deletePreviousChar()
                self.point -= 1
                self.line.remove(self.point, 1)
        elif key == QtCore.Qt.Key_Delete:
            #self.deleteChar()
            self.line.remove(self.point, 1)
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.moveCursor(cur.EndOfLine)
            self.point = self.line.length()
            self.insertPlainText('\n')
            if self.reading is True:
                self.reading = False
            else:
                self.__run()
        elif key == QtCore.Qt.Key_Tab:
            self.__insertText(text)
        elif key == QtCore.Qt.Key_Left:
            if self.point:
                self.moveCursor(cur.Left)
                self.point -= 1
        elif key == QtCore.Qt.Key_Right:
            if self.point < self.line.length():
                self.moveCursor(cur.Right)
                self.point += 1
        elif key == QtCore.Qt.Key_Home:
            e.ignore()
        elif key == QtCore.Qt.Key_End:
            self.moveCursor(cur.EndOfLine)
            self.point = self.line.length()
        elif key == QtCore.Qt.Key_Up:
            while self.point > 0:
                cur.deletePreviousChar()
                self.point -= 1
                self.line.remove(self.point, 1)
            self._history_point -= 1
            text = QtCore.QString(self._history[self._history_point])
            self.__insertText(text)
        elif key == QtCore.Qt.Key_Down:
            if self._history_point==0:
                e.ignore()
            while self.point > 0:
                cur.deletePreviousChar()
                self.point -= 1
                self.line.remove(self.point, 1)
            self._history_point += 1
            text = QtCore.QString(self._history[self._history_point])
            self.__insertText(text)
        else:
            e.ignore()
