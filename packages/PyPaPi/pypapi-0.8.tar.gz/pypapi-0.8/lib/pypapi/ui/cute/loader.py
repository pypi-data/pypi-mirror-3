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


from logging import getLogger
from PyQt4 import QtCore, QtGui
from PyQt4.uic import uiparser, properties
from PyQt4.uic.Loader.loader import DynamicUILoader
from PyQt4.uic.properties import Properties as BaseProperties

# Monkeypatch per redirigere il log del loader standard su
# un logger tutto suo, per poterlo disattivare
properties.logging = getLogger('pyqt')
uiparser.DEBUG = properties.logging.debug

HANDLER_NAME = 'handleNewWidget'

class Properties(BaseProperties):

    def setProperties(self, widget, elem):
        try:
            self.wclass = elem.attrib["class"]
        except KeyError:
            pass
        for prop in elem.findall("property"):
            if prop[0].text is None:
                continue
            propname = prop.attrib["name"]
            if hasattr(self, propname):
                getattr(self, propname)(widget, prop)
            else:
                if propname == 'column':
                    setattr(widget, 'column', self.convert(prop, widget))
                elif propname == 'entity':
                    setattr(widget, 'entity', self.convert(prop, widget))
                else:
                    getattr(widget, "set%s%s" % (propname[0].upper(), propname[1:]))(
                        self.convert(prop, widget))


class UILoader(DynamicUILoader):

    def __init__(self):
        super(UILoader, self).__init__()
        self.wprops = Properties(self.factory, QtCore, QtGui)
        self.widgetTreeItemHandlers['widget'] = self.__class__.createWidget

    def setupObject(self, clsname, parent, branch, is_attribute = True):

        # il metodo dell'ancestor viene eseguito senza l'assegnazione
        # del widget alla form
        widget = super(UILoader, self).setupObject(clsname, parent, branch, False)
        handler = getattr(self.toplevelWidget, HANDLER_NAME, False)
        if handler:
            handler(widget)
        return widget

    def createWidget(self, elem):
        """Override del metodo di PyQt4.uic.uiparser.UIParser al fine
        di mantenere intatta la catena dei parents in tutti i
        casi. Vedi codice commentato più avanti."""
        def widgetClass(elem):
            cls = elem.attrib["class"]
            if cls == "Line":
                return "QFrame"
            else:
                return cls

        self.column_counter = 0
        self.row_counter = 0
        self.first_item = True

        parent = self.stack.topwidget

#       Dopo alcune prove, non capisco la ragione di questa eccezione
#       alla regola, possibile che sia una reminiscenza Qt3?
#       XXX Da tenere d'occhio
#         if isinstance(parent, (QtGui.QToolBox, QtGui.QTabWidget,
#                                QtGui.QStackedWidget)):
#             parent = None


        self.stack.push(self.setupObject(widgetClass(elem), parent, elem))

        if isinstance(self.stack.topwidget, QtGui.QTableWidget):
            self.stack.topwidget.clear()
            self.stack.topwidget.setColumnCount(len(elem.findall("column")))
            self.stack.topwidget.setRowCount(len(elem.findall("row")))

        self.traverseWidgetTree(elem)
        widget = self.stack.popWidget()

        if self.stack.topIsLayout():
            self.stack.peek().addWidget(widget, *elem.attrib["grid-position"])

        if isinstance(self.stack.topwidget, QtGui.QToolBox):
            icon = self.wprops.getAttribute(elem, "icon")
            if icon is not None:
                self.stack.topwidget.addItem(widget, icon, self.wprops.getAttribute(elem, "label"))
            else:
                self.stack.topwidget.addItem(widget, self.wprops.getAttribute(elem, "label"))

            tooltip = self.wprops.getAttribute(elem, "toolTip")
            if tooltip is not None:
                self.stack.topwidget.setItemToolTip(self.stack.topwidget.indexOf(widget), tooltip)

        elif isinstance(self.stack.topwidget, QtGui.QTabWidget):
            icon = self.wprops.getAttribute(elem, "icon")
            if icon is not None:
                self.stack.topwidget.addTab(widget, icon, self.wprops.getAttribute(elem, "title"))
            else:
                self.stack.topwidget.addTab(widget, self.wprops.getAttribute(elem, "title"))

            tooltip = self.wprops.getAttribute(elem, "toolTip")
            if tooltip is not None:
                self.stack.topwidget.setTabToolTip(self.stack.topwidget.indexOf(widget), tooltip)

        elif isinstance(self.stack.topwidget, QtGui.QStackedWidget):
            self.stack.topwidget.addWidget(widget)

        elif isinstance(self.stack.topwidget, QtGui.QDockWidget):
            self.stack.topwidget.setWidget(widget)

        elif isinstance(self.stack.topwidget, QtGui.QMainWindow):
            if type(widget) == QtGui.QWidget:
                self.stack.topwidget.setCentralWidget(widget)
            elif isinstance(widget, QtGui.QToolBar):
                tbArea = self.wprops.getAttribute(elem, "toolBarArea")

                if tbArea is None:
                    self.stack.topwidget.addToolBar(widget)
                else:
                    if isinstance(tbArea, basestring):
                        tbArea = getattr(QtCore.Qt, tbArea)
                    else:
                        tbArea = QtCore.Qt.ToolBarArea(tbArea)

                    self.stack.topwidget.addToolBar(tbArea, widget)

                tbBreak = self.wprops.getAttribute(elem, "toolBarBreak")

                if tbBreak:
                    self.stack.topwidget.insertToolBarBreak(widget)

            elif isinstance(widget, QtGui.QMenuBar):
                self.stack.topwidget.setMenuBar(widget)
            elif isinstance(widget, QtGui.QStatusBar):
                self.stack.topwidget.setStatusBar(widget)
            elif isinstance(widget, QtGui.QDockWidget):
                dwArea = self.wprops.getAttribute(elem, "dockWidgetArea")
                self.stack.topwidget.addDockWidget(
                    QtCore.Qt.DockWidgetArea(dwArea), widget)


def loadUi(uifile, baseinstance=None):

    return UILoader().loadUi(uifile, baseinstance)
