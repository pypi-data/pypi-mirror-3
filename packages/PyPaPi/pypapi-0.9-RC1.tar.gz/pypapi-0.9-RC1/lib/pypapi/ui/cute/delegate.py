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


import time
from PyQt4 import QtGui
from PyQt4 import QtCore
from zope import schema
from zope.schema.interfaces import IIterableSource
from pypapi.ui.cute.variant import VariantConverter
from pypapi.ui.widgets.nullabledateedit import NullableDateEdit
from pypapi.ui.cute.interfaces import ISelectFormLite

DATE_FORMAT = '%d/%m/%Y'
DATETIME_FORMAT = '%d/%m/%Y %H:%M'

class Delegate(QtGui.QItemDelegate):
    """
    Delegato per personalizzare il layout delle QTableView
    """

    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        model = self.parent().model()
        field = model.columns[index.column()]
        if isinstance(field.context, schema.Datetime):
            editor = NullableDateEdit(parent)
            editor.setCalendarPopup(True)
        else:
            editor = QtGui.QLineEdit(parent)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        if isinstance(editor, NullableDateEdit):
            value = model.data(index, QtCore.Qt.DisplayRole).toDate()
            editor.setDate(value)
        elif ISelectFormLite.implementedBy(editor.__class__):
            # forse da preselezionare...
            pass
        else:
            value = unicode(model.data(index, QtCore.Qt.DisplayRole).toString())
            editor.setText(value)

    def setModelData(self, editor, model, index):
        if isinstance(editor, NullableDateEdit):
            value = QtCore.QVariant(editor.date)
        elif ISelectFormLite.implementedBy(editor.__class__):
            entity = editor.selection[0]
            value = QtCore.QVariant(editor.table_view.model().getEntityRow(entity))
        else:
            value = QtCore.QVariant(editor.text())
        model.setData(index, value)

    def updateEditorGeometry(self, editor, option, index):
        if ISelectFormLite.implementedBy(editor.__class__):
            pos = editor.parent().mapToGlobal(QtCore.QPoint(option.rect.x(), option.rect.y()))
            option.rect.setX(pos.x())
            option.rect.setY(pos.y() + option.rect.height())
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):

        assert index.isValid()
        painter.save()
        model = index.model()
        fm = painter.fontMetrics()

        value = model.data(index)
        if value is None:
            value = ''
        else:
            value = model.data(index).toString()
        flags = None
        icon = None
        if len(value) > 0 and value[0] == '[':
            flags = value.split(']')[0][1:]
            if len(flags)>0 and flags[0] == ':':
                icon = QtGui.QImage(flags)
                flags = None
                value = ' '
            else:
                value = QtCore.QString(str(value).split(']', 1)[1])
        if icon is not None:
            rect = QtCore.QRect(option.rect.x()+4, option.rect.y()+8, 16, 16)
            painter.drawImage(rect, icon)
            painter.drawText(option.rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter, value)
            painter.restore()
            return
        if flags is not None:
            if '*' in flags:
                painter.fillRect(option.rect, option.palette.midlight())
            if '-' in flags:
                option.font.setStrikeOut(True)
            if 'r' in flags and True:
                painter.fillRect(option.rect, painter.brush().color())
        columns = model.columns
        context = columns[index.column()].context
        if isinstance(context, schema.Datetime):
            try:
                s = VariantConverter(model.data(index)).to_str()
                if s != '':
                    # eventualmente prendo solo la parte con la data
                    s = s.split(' ')[0]
                    date = time.strftime(DATE_FORMAT, time.strptime(s, '%Y-%m-%d'))
                else:
                    date = ''
            except ValueError:
                date = ''
            painter.drawText(option.rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter, QtCore.QString(date))
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)
        painter.restore()

    def sizeHint(self, option, index):
        model = index.model()
        context = model.columns[index.column()].context
        hint = QtGui.QItemDelegate.sizeHint(self, option, index)
        if isinstance(context, schema.Datetime):
            text = index.data(QtCore.Qt.DisplayRole).toDate().toString('dd/MM/yyyy')
            fm = QtGui.QFontMetrics(option.fontMetrics)
            return QtCore.QSize(fm.width(text), hint.height())
        width = hint.width()
        if width > 500:
            width = 500
        return QtCore.QSize(width, hint.height())
