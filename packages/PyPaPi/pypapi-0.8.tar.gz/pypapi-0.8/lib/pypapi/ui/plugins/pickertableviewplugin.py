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


from PyQt4 import QtGui, QtDesigner

from pypapi.ui.widgets.pickertableview import PickerTableView
from pypapi.ui.resources.logo import logo_pixmap


class PickerTableViewPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    """
    """

    def __init__(self, parent = None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self.initialized = False

    def initialize(self, form_editor):
        if self.initialized:
            return

        property_editor = form_editor.propertyEditor()
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return PickerTableView(parent)

    def name(self):
        return "PickerTableView"

    def group(self):
        return "PyPaPi"

    def icon(self):
        return QtGui.QIcon(logo_pixmap)

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return ('<widget class="PickerTableView" name=\"pickerTableView\">\n'
                " <property name=\"whatsThis\" >\n"
                "  <string>TableView with picker</string>\n"
                " </property>\n"
                " <property name=\"quickInsertEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                " <property name=\"infoEnabled\" stdset=\"0\" >\n"
                "  <bool>true</bool>\n"
                " </property>\n"
                " <property name=\"openEnabled\" stdset=\"0\" >\n"
                "  <bool>true</bool>\n"
                " </property>\n"
                " <property name=\"addEnabled\" stdset=\"0\" >\n"
                "  <bool>true</bool>\n"
                " </property>\n"
                " <property name=\"delEnabled\" stdset=\"0\" >\n"
                "  <bool>true</bool>\n"
                " </property>\n"
                " <property name=\"autosearchEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                " <property name=\"autoinfoEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                "</widget>\n"
                )

    def includeFile(self):
        return "pypapi.ui.widgets.pickertableview"

