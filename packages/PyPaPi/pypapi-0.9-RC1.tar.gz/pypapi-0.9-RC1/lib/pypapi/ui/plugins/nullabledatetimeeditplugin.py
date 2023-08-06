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
from pypapi.ui.widgets.nullabledatetimeedit import NullableDateTimeEdit
from pypapi.ui.resources.logo import logo_pixmap

class NullableDataTimeEditPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent = None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return NullableDateTimeEdit(parent)

    def name(self):
        return "NullableDateTimeEdit"

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
        return ("<widget class=\"NullableDateTimeEdit\" name=\"nullableDateTimeEdit\">\n"
                " <property name=\"whatsThis\" >\n"
                "  <string>NullableDateTimeEdit.</string>\n"
                " </property>\n"
                "</widget>\n"
                )

    def includeFile(self):
        return "pypapi.ui.widgets.nullabledatetimeedit"
