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

import os
from PyQt4 import QtGui, QtCore
import zope.interface
from zope.component import getUtility
from pypapi.ui.cute.interfaces import IDataContext
from pypapi.wf.interfaces import IWorkFlowForm, IWorkFlow
from pypapi.ui.cute.loader import loadUi
import pypapi.ui.resources

DIR = os.path.split(__file__)[0]

class WorkFlowForm(QtGui.QDialog):

    zope.interface.implements(IWorkFlowForm)


    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        ui_file = ui = os.path.join(DIR, 'ui/workflow.ui')
        loadUi(ui_file, self)
        for w in self.children():
            if isinstance(w, (QtGui.QListWidget, QtGui.QToolButton, QtGui.QLabel, QtGui.QLineEdit,
                              QtGui.QTextEdit)):
                name = str(w.objectName())
                setattr(self, name, w)
        self.listWidget_definitions.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.listWidget_definitions,
          QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'), self.processDefinitionsContextMenu)
        self.listWidget_actives.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.listWidget_actives,
          QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'), self.processesContextMenu)
        self.listWidget_workitems.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.listWidget_workitems,
          QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'), self.workitemsContextMenu)
        self.connect(self.listWidget_actives,
          QtCore.SIGNAL('itemSelectionChanged()'), self.activeProcessSelected)
        self.connect(self.listWidget_left,
          QtCore.SIGNAL('itemSelectionChanged()'), self.leftActivitySelected)
        self.createActions()
        self.activity_workitems = {}
        self.refresh()

        # temporary event logger
#         def log_workflow(event):
#             if hasattr(event, 'object'):
#                 print event.object, type(event.object)
#                 self.textEdit_history.append(str(event))
#         from zope.event import subscribers
#         subscribers.append(log_workflow)


    def createActions(self):
        refresh = QtGui.QAction(QtGui.QIcon(":/icons/arrow_refresh.png"), "&Refresh list", self)
        self.connect(refresh, QtCore.SIGNAL('triggered()'), self.refresh)
        preview = QtGui.QAction(QtGui.QIcon(":/icons/chart_organisation.png"), "&Preview process", self)
        self.connect(preview, QtCore.SIGNAL('triggered()'), self.actionPreviewProcess)
        previewd = QtGui.QAction(QtGui.QIcon(":/icons/chart_organisation.png"), "&Preview process definition", self)
        self.connect(previewd, QtCore.SIGNAL('triggered()'), self.actionPreviewProcessDefinition)
        start = QtGui.QAction(QtGui.QIcon(":/icons/control_play_blue.png"), "&Start process", self)
        self.connect(start, QtCore.SIGNAL('triggered()'), self.actionStartProcess)
        execute = QtGui.QAction(QtGui.QIcon(":/icons/control_play_blue.png"), "&Execute workitem", self)
        self.connect(execute, QtCore.SIGNAL('triggered()'), self.actionExecuteWorkitem)
        self.processes_definitions_actions = dict(previewd=previewd, refresh=refresh, start=start)
        self.workitems_actions = dict(execute=execute,)
        self.processes_actions = dict(preview=preview,)


    def processDefinitionsContextMenu(self, pos):
        idx = self.listWidget_definitions.indexAt(pos)
        if not idx.isValid():
            return
        popup_menu = QtGui.QMenu(self)
        popup_menu.addAction(self.processes_definitions_actions['refresh'])
        popup_menu.addAction(self.processes_definitions_actions['previewd'])
        popup_menu.addAction(self.processes_definitions_actions['start'])
        action = popup_menu.exec_(self.listWidget_definitions.mapToGlobal(pos))


    def processesContextMenu(self, pos):
        idx = self.listWidget_actives.indexAt(pos)
        if not idx.isValid():
            return
        popup_menu = QtGui.QMenu(self)
        popup_menu.addAction(self.processes_actions['preview'])
        action = popup_menu.exec_(self.listWidget_actives.mapToGlobal(pos))


    def workitemsContextMenu(self, pos):
        idx = self.listWidget_workitems.indexAt(pos)
        if not idx.isValid():
            return
        popup_menu = QtGui.QMenu(self)
        popup_menu.addAction(self.workitems_actions['execute'])
        action = popup_menu.exec_(self.listWidget_workitems.mapToGlobal(pos))


    def refresh(self):
        wf = getUtility(IWorkFlow)
        entity = IDataContext(self.parent()).current_entity
        definitions = wf.processDefinitionsFromEntity(entity)
        self.listWidget_definitions.clear()
        self.listWidget_actives.clear()
        self.listWidget_left.clear()
        self.listWidget_workitems.clear()
        self.definitions_images = {}
        for pd, jpg in definitions:
            item = QtGui.QListWidgetItem(pd.description or pd.__name__)
            item.setToolTip(pd.description or '')
            self.definitions_images[pd.id] = jpg
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(pd.id))
            self.listWidget_definitions.addItem(item)
        if hasattr(entity, 'processes'):
            self.listWidget_actives.clear()
            for process in entity.processes:
                pd = process.definition
                item = QtGui.QListWidgetItem(pd.description or pd.__name__)
                item.setToolTip(pd.description or '')
                if process.active:
                    icon = QtGui.QIcon(":/icons/cog.png")
                else:
                    icon = QtGui.QIcon(":/icons/accept.png")
                item.setIcon(icon)
                self.listWidget_actives.addItem(item)


    def activeProcessSelected(self):
        i = self.listWidget_actives.currentRow()
        entity = IDataContext(self.parent()).current_entity
        process = entity.processes[i]
        if not process.active:
            return
        pd = process.definition
        # next activity
        #next_activity = process.activities[process.nextActivityId]
        #next_activity_definition = pd.activities[next_activity.activity_definition_identifier]
        #self.lineEdit_next.setText(next_activity_definition.__name__)
        # activities left
        self.listWidget_left.clear()
        for k in process.activities.keys():
            activity = process.activities[k]
            activity_definition = pd.activities[activity.activity_definition_identifier]
            item = QtGui.QListWidgetItem(activity_definition.__name__)
            item.setToolTip(activity_definition.description or '')
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(activity.id))
            self.listWidget_left.addItem(item)


    def leftActivitySelected(self):
        item = self.listWidget_left.currentItem()
        _id = int(item.data(QtCore.Qt.UserRole).toString())
        i = self.listWidget_actives.currentRow()
        entity = IDataContext(self.parent()).current_entity
        process = entity.processes[i]
        pd = process.definition
        self.listWidget_workitems.clear()
        try:
            activity = process.activities[_id]
        except KeyError:
            return
        self.activity_workitems = {}
        for k in activity.workitems.keys():
            workitem, _1, _2, _3 = activity.workitems[k]
            item = QtGui.QListWidgetItem(workitem.__doc__)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(workitem.id))
            self.listWidget_workitems.addItem(item)
            self.activity_workitems[workitem.id] = workitem


    def actionPreviewProcess(self):
        i = self.listWidget_actives.currentRow()
        entity = IDataContext(self.parent()).current_entity
        process = entity.processes[i]
        _id = process.process_definition_identifier
        file_name = self.definitions_images[_id]
        if file_name is None:
            pass
            # QMsgBox?
        label = QtGui.QLabel()
        pix = QtGui.QPixmap.fromImage(QtGui.QImageReader(file_name).read())
        painter = QtGui.QPainter(pix)
        pix_active = QtGui.QPixmap(":/icons/cog.png")
        for activity in process.activities.values():
            x, y = process.getPointFromActivity(activity)
            painter.drawPixmap(x, y, pix_active)
        painter.end()
        label.setPixmap(pix)
        label.resize(label.pixmap().size())
        label.show()
        self.label_preview_precess = label


    def actionPreviewProcessDefinition(self):
        item = self.listWidget_definitions.currentItem()
        _id = str(item.data(QtCore.Qt.UserRole).toString())
        file_name = self.definitions_images[_id]
        if file_name is None:
            pass
            # QMsgBox?
        label = QtGui.QLabel()
        pix = QtGui.QPixmap.fromImage(QtGui.QImageReader(file_name).read())
        label.setPixmap(pix)
        label.resize(label.pixmap().size())
        label.show()
        self.label_preview_precess = label


    def actionStartProcess(self):
        item = self.listWidget_definitions.currentItem()
        if item is None:
            return
        _id = str(item.data(QtCore.Qt.UserRole).toString())
        wf = getUtility(IWorkFlow)
        entity = IDataContext(self.parent()).current_entity
        proc = wf.createProcess(entity, _id)
        proc.start()
        self.refresh()


    def actionExecuteWorkitem(self):
        item = self.listWidget_workitems.currentItem()
        if item is None:
            return
        _id = int(item.data(QtCore.Qt.UserRole).toString())
        workitem = self.activity_workitems[_id]
        workitem.finish()
        self.refresh()
