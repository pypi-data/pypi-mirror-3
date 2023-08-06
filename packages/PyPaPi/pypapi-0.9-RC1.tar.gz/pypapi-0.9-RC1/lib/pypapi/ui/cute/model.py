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


from datetime import datetime, time
from logging import getLogger
from operator import or_
from PyQt4 import QtCore, QtGui
from zope.interface import implements, implementer
from zope.component import provideAdapter, adapts, getMultiAdapter, \
     getUtility, createObject, adapter
from zope.schema.interfaces import IInt, IField, IChoice, \
     ICollection, IBool, IObject, IDatetime, ITime
from pypapi.db.interfaces import IListStore
from pypapi.db.storage import SAListStore
from pypapi.ui.cute.variant import VariantConverter
from pypapi.ui.cute.interfaces import *

logger = getLogger('cute')

ITEM_FLAGS_NAME_MAP = {'enabled': QtCore.Qt.ItemIsEnabled,
                       'editable': QtCore.Qt.ItemIsEditable,
                       'selectable': QtCore.Qt.ItemIsSelectable,
                       'checkable': QtCore.Qt.ItemIsUserCheckable,
                       'drag_enabled': QtCore.Qt.ItemIsDragEnabled,
                       'drop_enabled': QtCore.Qt.ItemIsDropEnabled,
                       'tristate': QtCore.Qt.ItemIsTristate}

ITEM_ROLES_NAME_MAP = {QtCore.Qt.EditRole: 'edit',
                       QtCore.Qt.DisplayRole: 'display',
                       QtCore.Qt.ToolTipRole: 'tooltip',
                       QtCore.Qt.DecorationRole: 'decoration',
                       QtCore.Qt.TextAlignmentRole: 'alignment',
                       QtCore.Qt.CheckStateRole: 'checkstate',
                       }

PYPAPI_DND_MIMETYPE = "application/vnd.pypapi.entity"

class Item(object):

    implements(IDataItem)
    debug = False

    def __init__(self, column, value):

        self.column = column
        self.value = value
        self._flags = column.flags

    def _getDataContext(self):

        return IDataContext(self)

    dc = property(_getDataContext)

    def getFlags(self):

        return self._flags

    flags = property(getFlags)

    def getQFlags(self):

        qvalues = [ITEM_FLAGS_NAME_MAP[f] for f, v in self.flags.iteritems() if v is True]
        return reduce(or_,qvalues)

    def __getitem__(self, qt_data_role):

        meth_name = 'get%s' % ITEM_ROLES_NAME_MAP[qt_data_role].capitalize()
        method = getattr(self, meth_name, None)
        if method is None:
            result = QtCore.QVariant()
        else:
            result = method()
        if self.debug is True:
            logger.debug('Get del ruolo %r, risultato %r, valore main accessor %r',
                         meth_name, result, self.get())
        return result

    def get(self):

        if callable(self.value):
            return self.value()
        return self.value

    def getDisplay(self):

        try:
            value = self.get()
        except AttributeError:
            value = QtCore.QVariant(u'n.d.')
        if value is None:
            return QtCore.QVariant(u'')
        return QtCore.QVariant(unicode(value))

@adapter(IDataItem)
@implementer(IDataContext)
def itemDataContext(item):

    dc = IDataContext(item.column)
    return dc

provideAdapter(itemDataContext)


class EditableItem(Item):

    def __init__(self, column, value, setfunc, _type=unicode):

        super(EditableItem, self).__init__(column, value)
        self.value_type = _type
        self.setfunc = setfunc

    def set(self, value):

        self.setfunc(value)

    def __setitem__(self, qt_data_role, value):

        meth_name = 'set%s' % ITEM_ROLES_NAME_MAP[qt_data_role].capitalize()
        method = getattr(self, meth_name, None)
        if method is None:
            raise KeyError, "Il set per '%s' non è implementato." % meth_name
        method(value)
        if self.debug is True:
            logger.debug('Set del ruolo %r, valore %r, valore main accessor %r',
                         meth_name, value, self.get())

    def getEdit(self):

        try:
            value = self.get()
        except AttributeError:
            value = self.value_type()
        return QtCore.QVariant(value)

    def setEdit(self, value):

        self.set(VariantConverter(value).convert(self.value_type))


class FieldItem(EditableItem):

    adapts(IColumn, IField)

    def __init__(self, column, bound_field):

        super(FieldItem, self).__init__(column, bound_field.get,
                                        bound_field.set,
                                        bound_field._type)
        self.context = bound_field

    def get(self):

        obj = self.context.context
        try:
            return self.context.get(obj)
        except AttributeError:
            return None

    def getEdit(self):

        try:
            value = self.get()
        except AttributeError:
            value = None
        if value is None:
            _type = self.value_type or self.context._type or unicode
            try:
                value = _type()
            except TypeError:
                return QtCore.QVariant()
        return QtCore.QVariant(value)

    def set(self, value):
        if self.flags['editable']:
            obj = self.context.context
            self.context.set(obj, value)
            logger.debug("Set della colonna '%s', valore '%s'", self.column.name, value)
        else:
            logger.debug("Colonna '%s' non modificabile, non imposto valore '%s'", self.column.name, value)

provideAdapter(FieldItem)


class IntFieldItem(FieldItem):

    adapts(IColumn, IInt)

    def __init__(self, column, bound_field):

        super(IntFieldItem, self).__init__(column, bound_field)
        # il field ritorna (int, long) come tipo
        self.value_type = int

provideAdapter(IntFieldItem)


class Column(Item):

    implements(IColumn)

    _flags = {'enabled': True,
              'editable': False,
              'selectable': True,
              'checkable': False,
              'drag_enabled': True,
              'drop_enabled': True,
              'tristate': False}

    model = None

    def __init__(self, name, label='', description='', setname=None, _type=unicode, **flags):

        self.name = name
        if len(label) > 0:
            self.label = label
        else:
            self.label = name
        self.description = description
        self.setname = setname
        self.item_type = _type
        self._flags = dict(self._flags) # fai una copia dell'attributo sulla classe
        self._flags.update(flags)
        if self.setname is not None:
            self._flags['editable'] = True

    def getFlags(self):

        flags = dict(self._flags)
        col_can_edit = flags['editable']
        if self.model is not None:
            flags['editable'] = self.model.editable and col_can_edit
        return flags

    flags = property(getFlags)

    def get(self):

        return self.label

    def getTooltip(self):

        return QtCore.QVariant(self.description)

    def bind(self, store_item):

        read_accessor = getattr(store_item, self.name)
        if not callable(read_accessor):
            read_accessor = lambda : getattr(store_item, self.name)
        if self.setname is not None:
            write_accessor = getattr(store_item, self.setname)
            if not callable(write_accessor):
                write_accessor = lambda v: setattr(store_item, self.setname, v)
            return EditableItem(self, read_accessor, write_accessor, self.item_type)
        return Item(self, read_accessor)

    def bindModel(self, model):

        new_self = self.__class__.__new__(self.__class__)
        new_self.__dict__.update(self.__dict__)
        new_self.model = model
        return new_self

@adapter(IColumn)
@implementer(IDataContext)
def columnDataContext(column):

    dc = IDataContext(column.model)
    return dc

provideAdapter(columnDataContext)


class MapColumn(Column):
    """Una colonna che mappa il valore di un attributo alle singole istanze"""

    implements(IIndexedColumn)

    def __init__(self, name, label='', description='', setname=None, _type=unicode,**flags):
        super(MapColumn, self).__init__(name, label, description, setname, _type, **flags)
        self.keys = {}

    def bind(self, store_item):

        item = super(MapColumn, self).bind(store_item)
        # mappo sempre per stringa, una scelta orientata alla gui
        self.keys[str(item.get())] = store_item
        return item

class FieldColumn(Column):

    adapts(IField)

    def __init__(self, unbound_field, **flags):

        super(FieldColumn, self).__init__(unbound_field.__name__,
                                          unbound_field.title,
                                          unbound_field.description, **flags)
        self.context = unbound_field
        self._flags['editable'] = not unbound_field.readonly

    def __str__(self):

        return "%s sul campo '%s' nome: '%s'" % \
               (self.__class__.__name__, self.context, self.name)

    def bind(self, store_item):

        return getMultiAdapter((self, self.context.bind(store_item)), IDataItem)

# la registrazione è più elaborata perché FieldColumn implementa sia
# la IDataItem che la IColumn e non è possibile derivare
# automaticamente la correlazione
provideAdapter(FieldColumn, adapts=(IField,), provides=IColumn)

class LookupColumn(FieldColumn):

    display_col = None

    def setLookupColumn(self, display_col=None, model=None):

        self.lookup_model = model
        if display_col is not None:
            if isinstance(display_col, Column):
                self.display_col = display_col
            elif isinstance(display_col, str):
                self.display_col = model.getColumnByName(display_col)
        else:
            self.display_col = model.columns[0]

    def bindModel(self, model):

        new_self = super(LookupColumn, self).bindModel(model)
        if new_self.lookup_model is None:
            dc = IDataContext(new_self)
            sub_dc = dc.getDetailDataContext(new_self.context)
            new_self.lookup_model = sub_dc.lookup_model
        if new_self.display_col is None:
            new_self.display_col = new_self.lookup_model.columns[0]
        return new_self

    def _getLookupModel(self):
        dc = IDataContext(self)
        sub_dc = dc.getDetailDataContext(self.context)
        return sub_dc.lookup_model

    lookup_model = property(_getLookupModel)

provideAdapter(LookupColumn, adapts=(IChoice,), provides=IColumn)

#class ChoiceColumn(FieldColumn):

#    pass

#provideAdapter(ChoiceColumn, adapts=(IChoice,), provides=IColumn)

class RelationItem(FieldItem):

    def getIndexByEntity(self, entity):

        if entity is not None:
            try:
                lookup_store = self.column.lookup_model.store
            except AttributeError:
                return -1
            ix_entity = lookup_store.index(entity)
        else:
            ix_entity = -1
        return ix_entity

    def getEntityByIndex(self, index):

        try:
            lookup_store = self.column.lookup_model.store
        except AttributeError:
            index = -1
        if index >= 0:
            entity = lookup_store[index]
        else:
            entity = None
        return entity

    def getRelationItem(self, entity):

        lookup_model = self.column.lookup_model
        lookup_item = lookup_model.getByEntity(entity,
                                               self.column.display_col)
        return lookup_item


class LookupItem(RelationItem):

    adapts(IColumn, IChoice)

    def getDisplay(self):

        entity = self.get()
        if entity is None:
            return super(LookupItem, self).getDisplay()
        lookup_item = self.getRelationItem(entity)
        return lookup_item.getDisplay()

    def getEdit(self):

        entity = self.get()
        ix_entity = self.getIndexByEntity(entity)
        return QtCore.QVariant(ix_entity)

    def setEdit(self, value):

        selection_ix = int(VariantConverter(value))
        entity = self.getEntityByIndex(selection_ix)
        self.set(entity)

provideAdapter(LookupItem)


class BoolFieldItem(FieldItem):

    adapts(IColumn, IBool)

    def __init__(self, column, bound_field):

        super(BoolFieldItem, self).__init__(column, bound_field)
        self.value_type = bool
        self._flags['checkable'] = True

    def getCheckstate(self):

        value = self.value_type(self.get())
        if value == True:
            value = QtCore.Qt.Checked
        else:
            value = QtCore.Qt.Unchecked
        return QtCore.QVariant(value)

    def setCheckstate(self, value):

        value = int(VariantConverter(value))
        if value == QtCore.Qt.Checked:
            value = True
        else:
            value = False
        self.set(value)

    def getDisplay(self):

        return QtCore.QVariant(u'')

provideAdapter(BoolFieldItem)


class DatetimeFieldItem(FieldItem):

    adapts(IColumn, IDatetime)

    def __init__(self, column, bound_field):

        super(DatetimeFieldItem, self).__init__(column, bound_field)
        self.value_type = datetime

    def getEdit(self):
        try:
            value = self.get()
        except AttributeError:
            value = None
        if value is not None:
            value = QtCore.QDateTime(value)
        return QtCore.QVariant(value)

    def setEdit(self, value):
        super(DatetimeFieldItem, self).setEdit(value)

provideAdapter(DatetimeFieldItem)


class TimeFieldItem(FieldItem):

    adapts(IColumn, ITime)

    def __init__(self, column, bound_field):

        super(TimeFieldItem, self).__init__(column, bound_field)
        self.value_type = time

    def getEdit(self):
        try:
            value = self.get()
        except AttributeError:
            value = None
        if value is not None:
            value = QtCore.QTime(value)
        return QtCore.QVariant(value)

    def setEdit(self, value):

        super(TimeFieldItem, self).setEdit(value)

provideAdapter(TimeFieldItem)


class DetailColumn(FieldColumn):

    adapts(IColumn, ICollection)

    def __init__(self, unbound_field, **flags):

        super(DetailColumn, self).__init__(unbound_field, **flags)
        self._flags['editable'] = False

provideAdapter(DetailColumn, adapts=(ICollection,), provides=IColumn)


class DetailItem(FieldItem):

    adapts(IColumn, ICollection)

    def getDisplay(self):

        det_len = len(self.get())
        if det_len == 0:
            label = u'nessun elemento'
        elif det_len == 1:
            label = u'1 elemento'
        elif det_len > 1:
            label = u'%d elementi' % det_len
        return QtCore.QVariant(label)

provideAdapter(DetailItem)


class ObjectColumn(FieldColumn):


    def __init__(self, unbound_field, display_field='caption',  **flags):

        super(ObjectColumn, self).__init__(unbound_field, **flags)
        self.display_field = display_field

provideAdapter(ObjectColumn, adapts=(IObject,), provides=IColumn)


class ObjectItem(FieldItem):

    adapts(IColumn, IObject)

    def _getDisplayItem(self):

        detail_dc = self.dc.getDetailDataContext(self.context)
        field = detail_dc.interface.get(self.display_field)
        column = IColumn(field)
        item = column.bind(detail_dc.current_entity)
        return item

    def getDisplay(self):

        return self._getDisplayItem.getDisplay()

    def getEdit(self):

        return self.get()

    def setEdit(self, value):

        detail_dc = self.dc.getDetailDataContext(self.context)
        detail_dc.store.append(value)
        detail_dc.model.reset()

provideAdapter(ObjectItem)

class TableModel(QtCore.QAbstractTableModel):

    implements(IModel)
    resizable = True
    editable = True

    def __init__(self, store, parent=None, factory=None, columns=None):

        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cache = {}
        self._ix_cache = {}
        self._parent_field = None
        self._parent_model = None
        self.factory = factory
        if columns:
            self.columns = columns
        self.store = store

    def _purgeItemCache(self, entity=None, column=None):

        if entity is None and column is None:
            self._cache = {}
        elif entity and column is None:
            cache = self._cache
            columns = self._columns
            for column in columns:
                if cache.has_key((entity, column)):
                    del cache[(entity, column)]

    def _purgeIndexCache(self, entity=None, column=None):

        if entity is None and column is None:
            self._ix_cache = {}
        elif entity and column is None:
            cache = self._ix_cache
            columns_indexes = range(len(self._columns))
            for column in columns_indexes:
                if cache.has_key((entity, column)):
                    del cache[(entity, column)]

    def _canCreate(self):

        return self.factory is not None

    def _setColumns(self, columns):

        bound_columns = [col.bindModel(self) for col in columns]
        self._columns = bound_columns
        self.reset()

    def _getColumns(self):

        return tuple(self._columns)

    columns = property(_getColumns, _setColumns)

    def _setStore(self, store):

        self._purgeIndexCache()
        self._purgeItemCache()
        self._store = store
        self.reset()

    def _getStore(self):

        return self._store

    store = property(_getStore, _setStore)

    #####
    ## PyPaPi specific API
    #####

    def get(self, ix_row, ix_column):

        entity = self.store[ix_row]
        column = self._columns[ix_column]
        return self.getByEntity(entity, column)

    def getByColumn(self, ix_row, column):

        col_ix = self._columns.index(column)
        return self.get(ix_row, col_ix)

    def getByEntity(self, entity, column):

        cache = self._cache
        try:
            result = cache[(entity, column)]
        except KeyError:
            result = cache[(entity, column)] = column.bind(entity)
        return result

    def getColumnByName(self, col_name):

        for column in self._columns:
            if column.name == col_name:
                return column
        raise ValueError, "Nessuna colonna con questo nome: '%s'" % col_name

    def getColumnIndex(self, col_name):

        col = self.getColumnByName(col_name)
        return self._columns.index(col)

    def getEntityRow(self, entity):

        return self.store.index(entity)

    def getEntityByRow(self, ix_row):

        return self.store[ix_row]

    def create(self, data={}):

        if self.factory is None:
            raise ValueError('La factory non è definita')
        factory_id, creation_args = self.factory
        args, kwargs = creation_args
        new_entity = createObject(factory_id, *args, **kwargs)
        for k,v in data.iteritems():
            setattr(new_entity, k, v)
        return new_entity

    def setParentBinding(self, model, field):

        self._parent_field = field
        self._parent_model = model

    def setParentIndex(self, row):

        field = self._parent_field
        parent_entity = self._parent_model.getEntityByRow(row)
        value = field.bind(parent_entity).get(parent_entity)
        self.store = value

    def setParentModelIndex(self, index):

        self.setParentIndex(index.row())


    #####
    ## Qt QAbstractItemModel API
    #####

    def index(self, row, column, parent=QtCore.QModelIndex()):

        assert not parent.isValid()
        if (row < 0) or  (row > len(self.store)-1) or \
           (column > len(self._columns)):
            return QtCore.QModelIndex()
        item = self.get(row, column)
        entity = self.store[row]
        if self._ix_cache.has_key((entity, column)):
            return self._ix_cache[(entity, column)]
        else:
            ix = self.createIndex(row, column, item)
            self._ix_cache[(entity, column)] = ix
            return ix

    def rowCount(self, parent=QtCore.QModelIndex()):

        if parent.isValid():
            return False
        return len(self.store)

    def columnCount(self, parent=QtCore.QModelIndex()):

        if parent.isValid():
            return False
        return len(self._columns)

    def flags(self, index):

        if index.isValid():
            item = index.internalPointer()
            return item.getQFlags()
        return QtCore.Qt.ItemIsDropEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):

        if orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        try:
            col = self._columns[section]
            value = col[role]
        except KeyError:
            return QtCore.QVariant()
        return value

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return QtCore.QVariant()
        item = index.internalPointer()
        try:
            value = item[role]
        except KeyError:
            return QtCore.QVariant()
        return value

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if not index.isValid():
            return False
        if isinstance(value, QtCore.QVariant) and not value.isValid():
            return False
        item = index.internalPointer()
        try:
            old_value = item[role]
            if old_value != value:
                item[role] = value
                self.emit(QtCore.SIGNAL('dataChanged(const QModelIndex, const QModelIndex)'), index, index)
        except KeyError:
            return False
        except Exception:
            logger.exception("Errore durante il set della colonna '%s', modello '%s', valore '%s'",
                             item.column.name, IDataContext(self).name, value)
            return False
        return True

    def removeRows(self, position, count, parent=QtCore.QModelIndex()):

        if not self.resizable:
            return False
        rows_indexes = range(position, position+count)
        self.beginRemoveRows(parent, rows_indexes[0], rows_indexes[-1])
        rows_reversed = rows_indexes[:]
        rows_reversed.reverse()
        self._purgeIndexCache()
        for row in rows_reversed:
            entity = self.store[row]
            self._purgeItemCache(entity)
            self.store.pop(row)
        self.endRemoveRows()
        return True

    def insertRows(self, position, count, parent=QtCore.QModelIndex(), entities=None):

        if not self.resizable and not self._canCreate():
            return False
        if position <= -1:
            position = len(self.store)
        rows_indexes = range(position, position+count)
        self.beginInsertRows(parent, rows_indexes[0], rows_indexes[-1])
        self._purgeIndexCache()
        for idx,rown in enumerate(rows_indexes):
            if entities is not None:
                new_item = entities[idx]
            else:
                new_item = self.create()
            self.store.insert(position, new_item)
        self.endInsertRows()
        return True

    def sort(self, column, order=QtCore.Qt.AscendingOrder):

        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        attr = self.columns[column].name
        key = lambda x: getattr(x, attr)
        self.store.sort(key=key, reverse=order)
        self._purgeIndexCache()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


    #####
    ## Drag&drop
    #####

    def mimeData(self, indexes):
        "Estrai la selezione di cui si sta facendo il drag"

        mime_data = QtCore.QMimeData()

        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)

        # Impacchetta nello stream le posizioni degli elementi
        # selezionati e trascinati: non usare un set, per mantenere
        # l'ordine di selezione
        rows = []
        for idx in indexes:
            row = idx.row()
            if not row in rows:
                rows.append(row)
        for row in rows:
            stream << QtCore.QVariant(row)

        mime_data.setData(PYPAPI_DND_MIMETYPE, encoded_data)

        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        "Accetta l'azione di drop"

        if not data.hasFormat(PYPAPI_DND_MIMETYPE):
            return False

        if action == QtCore.Qt.IgnoreAction:
            return True

        if not parent.isValid() and row < 0:
            end_row = len(self.store)
        elif not parent.isValid():
            end_row = min(row, len(self.store))
        else:
            end_row = parent.row()

        encoded_data = data.data(PYPAPI_DND_MIMETYPE)
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        # Per ciascun elemento trascinato, rimuovilo dalla sua
        # posizione originale e reinseriscilo a partire dalla
        # posizione di drop

        moved_items = []
        moved_rows = []
        adj_end_row = 0

        # Copia dapprima gli elementi nelle posizioni selezionate

        while not stream.atEnd():
            drag_row = QtCore.QVariant()
            stream >> drag_row
            drag_row = int(VariantConverter(drag_row))
            moved_rows.append(drag_row)
            moved_items.append(self.store[drag_row])
            # Se stiamo spostando "in avanti", la posizione finale
            # deve essere aggiustata per tener conto degli elementi
            # eliminati
            if drag_row<end_row:
                adj_end_row += 1

        # Elimina gli elementi, a partire dall'ultima posizione

        moved_rows.sort()
        while moved_rows:
            self.removeRows(moved_rows.pop(), 1)

        # Aggiusta la posizione finale

        end_row -= adj_end_row

        # Reinserisci tutti gli elementi nell'ordine di selezione
        # a partire dalla posizione di drop

        for item in moved_items:
            self.insertRows(end_row, 1, entities=[item])
            end_row += 1

        self._purgeIndexCache()
        self._purgeItemCache()
        self.reset()

        return True

    def supportedDropActions(self):
        "Ritorna il tipo di drop action supportate"

        return QtCore.Qt.MoveAction

    def mimeTypes(self):
        "Ritorna la lista dei `mimetypes` supportati dal modello"

        types = QtCore.QStringList()
        types << PYPAPI_DND_MIMETYPE
        return types


provideAdapter(TableModel, (IListStore, None), IModel)


class TreeItem(object):
    """
    TreeItem mi presenta il singolo item all'interno del modello TreeModel
    """

    def __init__(self, data, entity=None, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.itemEntity = entity
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def row(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return QtCore.QVariant(self.itemData[column])

    def parent(self):
        return self.parentItem


class TreeModel(QtCore.QAbstractItemModel):

    implements(ITreeModel, IModel)

    def __init__(self, model, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._table_model = model
        self._initRootItem()

    def _initRootItem(self):
        rootData = [c.label for c in self.columns]
        self.rootItem = TreeItem(rootData)

    def _setColumns(self, columns):
        self._table_model._setColumns(columns)
    def _getColumns(self):
        return self._table_model._getColumns()
    columns = property(_getColumns, _setColumns)

    def _setStore(self, store):
        self._table_model._setStore(store)
        self.setupTreeModelData(store)
        self.reset()
    def _getStore(self):
        return self._table_model._getStore()
    store = property(_getStore, _setStore)

    def get(self, ix_row, ix_column):
        return self._table_model.get(ix_row, ix_column)

    def getEntityByRow(self, ix_row):
        return self._table_model.getEntityByRow(ix_row)

    def _setParentAttribute(self, attribute):
        self._parent_attribute = str(attribute)
        ixs = [ix for ix in range(len(self.columns)) if self.columns[ix].name == attribute]
        if len(ixs) == 1:
            self._ix_parentattribute = ixs[0]
        else:
            logger.exception("Errore durante la determinazione dell'ID padre '%s'", attribute)
    def _getParentAttribute(self):
        return self._parent_attribute
    parent_attribute = property(_getParentAttribute, _setParentAttribute)

    def _setChildAttribute(self, attribute):
        self._child_attribute = attribute
        ixs = [ix for ix in range(len(self.columns)) if self.columns[ix].name == attribute]
        if len(ixs) == 1:
            self._ix_childattribute = ixs[0]
        else:
            logger.exception("Errore durante la determinazione dell'ID figlio '%s'", attribute)
    def _getChildAttribute(self):
        return self._child_attribute
    child_attribute = property(_getChildAttribute, _setChildAttribute)

    def setupTreeModelData(self, store):
        items = {}
        self._initRootItem()
        for ix_row in range(len(store)):
            entity = store[ix_row]
            row = [self.get(ix_row, ix_column) for ix_column in range(len(self.columns))]
            parent_id = self.get(ix_row, self._ix_parentattribute).get()
            if parent_id is None:
                parent_item = self.rootItem
            else:
                parent_item = items[parent_id]
            item = TreeItem(row, entity, parent_item)
            parent_item.appendChild(item)
            items[self.get(ix_row, self._ix_childattribute).get()] = item

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def flags(self, index):
        if not index.isValid():
            return 0
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)
        else:
            return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        item = index.internalPointer().itemData[index.column()]
        try:
            value = item[role]
        except KeyError:
            return QtCore.QVariant()
        return value

    def insertRows(self, position, count, parent=QtCore.QModelIndex(), entities=None):
        parent_item = parent.internalPointer()
        if parent_item is not None:
            position = parent_item.childCount()
        else:
            parent_item = self.rootItem
            position = 0
        rows_indexes = range(position, position+count)
        self.beginInsertRows(parent, rows_indexes[0], rows_indexes[-1])
        for idx,rown in enumerate(rows_indexes):
            if entities is not None:
                new_entity = entities[idx]
            else:
                new_entity = self.create()
            if parent.isValid():
                id_parent = parent_item.itemData[self._ix_childattribute].get()
                _type = parent_item.itemData[self._ix_parentattribute].value_type
                setattr(new_entity, self.parent_attribute, _type(id_parent))
            self.store.append(new_entity)
            row = [self.get(-1, ix_column) for ix_column in range(len(self.columns))]
            child_item = TreeItem(row, new_entity, parent_item)
            parent_item.appendChild(child_item)
        self.endInsertRows()
        # 'sporco' il pdc
        pdc = getUtility(IDataContext, '.', IDataContext(self._table_model))
        pdc.is_dirty = True
        return True

@adapter(IModel)
@implementer(ITreeModel)
def tableModelTreeModel(model):
    tree_model = TreeModel(model)
    return tree_model
provideAdapter(tableModelTreeModel)


class StandardLookupModel(TableModel):

    def __init__(self, field, parent=None):

        columns = [Column('getCaption', field.title)]
        TableModel.__init__(self, [], parent, columns=columns)
        self.resizable = False
        self.editable = False


class DetailModel(TableModel):

    def __init__(self, field, parent=None, factory=None, columns=None):

        TableModel.__init__(self, [], parent, factory, columns)
        self._parent_field = field
        self._parent_entity = None

    def setParentEntity(self, parent_entity):

        field = self._parent_field
        value = field.bind(parent_entity).get(parent_entity)
        self.store = value
        self._parent_entity = entity

provideAdapter(DetailModel, (ICollection, None), IModel)

'''
class SingleItemDetailModel(DetailModel):
    """Versione di TableModel da utilizzare nel caso di relazione 1-1"""

    def _setStore(self, item):

        self._store = SAListStore(disable_session=True)
        if item is not None:
            self._store.append(item)

    def _getStore(self):

        return self._store

    store = property(_getStore, _setStore)

    def removeRows(self, position, count, parent=QtCore.QModelIndex()):

        # l'uso di super() potrebbe essere pericoloso anche in questo
        # caso? vedi doc pyqt4
        result = super(SingleItemDetailModel, self).removeRows(position, count,
                                                               parent)
        if result is True:
            self.setEntity(None)

    def insertRows(self, position, count, parent=QtCore.QModelIndex()):

        if count > 1 or len(self.store) >= 1:
            return False
        result = super(SingleItemDetailModel, self).insertRows(position, count,
                                                               parent)
        if result is True:
            self.setEntity(self.store[0])

    def setEntity(self, value):

        parent_entity = self._parent_entity
        field = self._parent_field
        bound_field = field.bind(parent_entity)
        bound_field.set(parent_entity, value)

provideAdapter(SingleItemDetailModel, (IChoice, None), IModel)
'''

@adapter(IModel)
@implementer(IDataContext)
def modelDataContext(model):

    dc = QtCore.QObject.parent(model)
    return dc

provideAdapter(modelDataContext)


def test_Column_and_Item():

    class Value(object):
        pass
    o = Value()
    o.testvalue = 99
    column = Column('testvalue', 'Test Column', 'This is a test Column', drag_enabled=True)
    # i valori dei vari ruoli Qt possono essere direttamente richiesti come items
    assert column[QtCore.Qt.DisplayRole] == QtCore.QVariant('Test Column')
    assert column[QtCore.Qt.DecorationRole] == QtCore.QVariant()
    assert column[QtCore.Qt.ToolTipRole] == QtCore.QVariant('This is a test Column')
    # i flags sono valorizzabili alla maniera standard Qt
    assert column.flags['drag_enabled']  is True
    assert column.getQFlags() == (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
    item = column.bind(o)
    assert item.get() == 99
    # l'item deriva i propri flags dalla colonna
    assert item.getQFlags() == (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
    assert item[QtCore.Qt.DisplayRole] == QtCore.QVariant(unicode(99))
    assert item[QtCore.Qt.EditRole] == QtCore.QVariant()
    assert item[QtCore.Qt.ToolTipRole] == QtCore.QVariant()

def test_EditableItem():

    class Value(object):
        pass
    o = Value()
    o.testvalue = 99
    column = Column('testvalue', setname='testvalue', _type=int)
    item = column.bind(o)
    item.set(100)
    assert item.get() == 100

    item[QtCore.Qt.EditRole] = QtCore.QVariant(150)
    assert item.get() == 150

    item[QtCore.Qt.EditRole] = QtCore.QVariant('120')
    assert item.get() == 120
    raise_called = False
    try:
        item[QtCore.Qt.DisplayRole] = QtCore.QVariant('200')
    except KeyError:
        raise_called = True
    assert raise_called is True
    assert item.getQFlags() == (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

def test_FieldColumn_and_FieldItem():

    from pypapi.db.interfaces import IUtente, IDatabase
    from pypapi.db.model import Utente
    cod_utente = IUtente.get('cod_utente')
    id_utente = IUtente.get('id_utente')
    db = getUtility(IDatabase)
    db.open('sqlite:///procedimenti.sqlite')

    utente = db.session.query(Utente).first()
    assert isinstance(utente, Utente)

    col_cod_u = IColumn(cod_utente)
    col_id_u = IColumn(id_utente)
    assert isinstance(col_cod_u, FieldColumn)
    assert col_cod_u.context == cod_utente

    it_cod_u = col_cod_u.bind(utente)
    it_id_u = col_id_u.bind(utente)
    assert isinstance(it_cod_u, IntFieldItem)
    assert isinstance(it_id_u, FieldItem)
    assert it_cod_u[QtCore.Qt.EditRole] == QtCore.QVariant(utente.cod_utente)
    assert it_cod_u[QtCore.Qt.DisplayRole] == QtCore.QVariant(unicode(utente.cod_utente))

    it_cod_u[QtCore.Qt.EditRole] = QtCore.QVariant(150)
    assert utente.cod_utente == 150
    db.close()

def test_LookupColumn_and_LookupItem():

    from pypapi.db.interfaces import IIterProcedurale, IDatabase
    from pypapi.db.model import IterProcedurale
    from pypapi.db.storage import SAListStore
    from zope.schema import getFieldsInOrder
    ente = IIterProcedurale.get('ente')
    db = getUtility(IDatabase)
    db.open('sqlite:///procedimenti.sqlite')
    iter_proc = SAListStore(db.session.query(IterProcedurale))
    enti = SAListStore(IIterProcedurale.get('ente').source(IterProcedurale))

    class IterProcModel(TableModel):
        # tolgo gli ultimi 3 campi perché sono IList e non sono ancora supportati
        columns = [IColumn(field) for name, field in getFieldsInOrder(IIterProcedurale)][:-3]

    class EnteModel(TableModel):
        columns = [Column('getCaption', 'Enti')]

    ip_model = IterProcModel(iter_proc)
    e_model = EnteModel(enti)
    col_ente = ip_model.getColumnByName('ente')
    col_ente.setLookupModel(e_model, 'getCaption')
    entity = iter_proc[0]
    ip_item = col_ente.bind(entity)
    assert col_ente.lookup_model is e_model
    assert col_ente.display_col is e_model.columns[0]
    # setto un valore iniziale per test perché nei dati demo questo
    # campo è vuoto
    ip_item.set(enti[0])
    assert ip_item.getDisplay() == QtCore.QVariant(entity.ente.getCaption())
    assert ip_item.getEdit() == QtCore.QVariant(enti.index(entity.ente))
