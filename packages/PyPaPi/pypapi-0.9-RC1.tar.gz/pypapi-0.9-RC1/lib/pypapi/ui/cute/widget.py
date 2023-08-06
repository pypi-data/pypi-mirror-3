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

from zope.interface import classImplements, implementer
from zope.component import adapter, provideAdapter, provideHandler, getUtility
from zope.component.interfaces import IComponentLookup
from zope.schema import getFields
from PyQt4 import QtGui, QtCore
from pypapi.db.interfaces import EXPAND, COLLAPSE
from pypapi.ui.cute import interfaces

classImplements(QtCore.QObject, interfaces.IObject)
classImplements(QtGui.QWidget, interfaces.IWidget)
classImplements(QtGui.QLineEdit, interfaces.ISimpleDataWidget)
classImplements(QtGui.QSpinBox, interfaces.ISimpleDataWidget)
classImplements(QtGui.QTextEdit, interfaces.ISimpleDataWidget)
classImplements(QtGui.QCheckBox, interfaces.ISimpleDataWidget)
classImplements(QtGui.QDateTimeEdit, interfaces.ISimpleDataWidget)
classImplements(QtGui.QTimeEdit, interfaces.ISimpleDataWidget)
#classImplements(QtGui.QComboBox, interfaces.ISimpleDataWidget)
classImplements(QtGui.QComboBox, interfaces.ILookupDataWidget)
classImplements(QtGui.QAbstractItemView, interfaces.IModelView)

logger = getLogger('cute')

@adapter(interfaces.IObject)
@implementer(IComponentLookup)
def resolveRegistry(obj):
    """Dato un qualsiasi oggetto IObject, ricerca e restituisce se
    possibile il parent che implementa l'api del registro di
    componenti zope. Per ora, solo form.BasicForm implementa questa
    funzionalità."""
    while not IComponentLookup.providedBy(obj):
        if obj is None:
            raise TypeError('Registro non trovato nella catena dei parents')
        try:
            obj = obj.parent()
        except:
            logger.exception("Can't get parent of %r", obj)
            raise
    return obj

provideAdapter(resolveRegistry)

@adapter(interfaces.IObject)
@implementer(interfaces.IDataContext)
def objectDataContext(qobject):
    """Dato un IObject, calcola il contesto dati di tale oggetto. Tale
    informazione è generalmente acquisita dal parent, ma può essere
    impostato tramite una property di nome 'entity' impostata sul
    widget stesso."""
    dc_hint = getattr(qobject, 'entity', None)
    if isinstance(dc_hint, QtCore.QString):
        dc_hint = str(dc_hint)
    if dc_hint is not None and isinstance(dc_hint, basestring):
        dc = getUtility(interfaces.IDataContext, dc_hint, qobject)
    else:
        dc = interfaces.IDataContext(QtCore.QObject.parent(qobject))
    return dc

provideAdapter(objectDataContext)

@adapter(interfaces.IModelView, interfaces.IWidgetCreationEvent)
def modelViewBinding(view, event):

    excepts = (QtGui.QListWidget, QtGui.QTableWidget)
    dc = interfaces.IDataContext(view)
    if isinstance(view, QtGui.QTreeView) or interfaces.ITreeModelView.providedBy(view):
        model = interfaces.ITreeModel(dc.model)
        model.parent_attribute = view.parentAttribute
        model.child_attribute = view.childAttribute
        dc.model = model
        dc.mapper.setModel(model)
        view.setModel(model)
        view.setSelectionModel(dc.selection_model)
    elif not isinstance(view, excepts):
        model = dc.model
        view.setModel(model)
        view.setSelectionModel(dc.selection_model)
        setupTableHeaders(dc, view)

provideHandler(modelViewBinding)

def setupTableHeaders(dc, view):
    """Configura gli headers delle colonne della tabella in
    accordo con gli hints sui campi."""
    cols = dc.model.columns
    header = view.horizontalHeader()
    if header:
        for ix, c in enumerate(cols):
            try:
                layout = c.context.getTaggedValue('layout')
            except KeyError:
                layout = COLLAPSE
            if layout == COLLAPSE:
                header.setResizeMode(ix, QtGui.QHeaderView.ResizeToContents)
            elif layout == EXPAND:
                header.setResizeMode(ix, QtGui.QHeaderView.Stretch)

def resolveColumn(data_widget, dc):
    # strategia differenziata per trovare, se necessario, il valore
    # della colonna
    col_index = None
    col_name = getattr(data_widget, 'column', None)
    if col_name is None:
        try_col = str(data_widget.objectName())
        if try_col in getFields(dc.interface):
            col_name = try_col
    if col_name is not None:
        # in questo caso col_name è una QString
        col_name = str(col_name)
        col_index = dc.model.getColumnIndex(col_name)
    return col_index, col_name

@adapter(interfaces.ISimpleDataWidget, interfaces.IWidgetCreationEvent)
def simpleDWBinding(data_widget, event):

    dc = interfaces.IDataContext(data_widget)
    col_index = resolveColumn(data_widget, dc)[0]
    if col_index is not None:
        if isinstance(data_widget, QtGui.QTextEdit):
            dc.mapper.addMapping(data_widget, col_index, 'plainText')
        elif isinstance(data_widget, QtGui.QTimeEdit):
            dc.mapper.addMapping(data_widget, col_index, 'time')
        else:
            dc.mapper.addMapping(data_widget, col_index)

provideHandler(simpleDWBinding)


@adapter(interfaces.ILookupDataWidget, interfaces.IWidgetCreationEvent)
def lookupDWBinding(data_widget, event):

    dc = interfaces.IDataContext(data_widget)
    col_index, col_name = resolveColumn(data_widget, dc)
    if col_index is not None:
        detail_dc = dc.getDetailDataContext(col_name)
        data_widget.setModel(detail_dc.lookup_model)
        dc.mapper.addMapping(data_widget, col_index, 'currentIndex')

provideHandler(lookupDWBinding)
