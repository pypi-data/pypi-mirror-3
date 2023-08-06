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
from pypapi.ui.widgets.pickerentity import PickerEntity
from pypapi.ui.resources.logo import logo_pixmap


class PickerEntityPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    """
    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    # The __init__() method is only used to set up the plugin and define its
    # initialized variable.
    def __init__(self, parent = None):
    
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)

        self.initialized = False

    # The initialize() and isInitialized() methods allow the plugin to set up
    # any required resources, ensuring that this can only happen once for each
    # plugin.
    def initialize(self, core):

        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):

        return self.initialized

    # This factory method creates new instances of our custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        return PickerEntity(parent)

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "PickerEntity"

    # Returns the name of the group in Qt Designer's widget box that this
    # widget belongs to.
    def group(self):
        return "PyPaPi"

    # Returns the icon used to represent the custom widget in Qt Designer's
    # widget box.
    def icon(self):
        return QtGui.QIcon(logo_pixmap)

    # Returns a short description of the custom widget for use in a tool tip.
    def toolTip(self):
        return ""

    # Returns a short description of the custom widget for use in a "What's
    # This?" help message for the widget.
    def whatsThis(self):
        return ""

    # Returns True if the custom widget acts as a container for other widgets;
    # otherwise returns False. Note that plugins for custom containers also
    # need to provide an implementation of the QDesignerContainerExtension
    # interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False

    # Returns an XML description of a custom widget instance that describes
    # default values for its properties. Each custom widget created by this
    # plugin will be configured using this description.
    def domXml(self):
        return ("<widget class=\"PickerEntity\" name=\"pickerEntity\">\n"
                " <property name=\"whatsThis\" >\n"
                "  <string>PickerEntity.</string>\n"
                " </property>\n"
                " <property name=\"autosearchEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                " <property name=\"openEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                " <property name=\"liteModeEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                " <property name=\"nullItemEnabled\" stdset=\"0\" >\n"
                "  <bool>false</bool>\n"
                " </property>\n"
                "</widget>\n"
                )

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return "pypapi.ui.widgets.pickerentity"
