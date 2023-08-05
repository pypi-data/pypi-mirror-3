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


from datetime import date
from logging import getLogger
from sqlalchemy.orm import object_session
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.orderinglist import OrderingList
from sqlalchemy.exc import InvalidRequestError, InternalError, IntegrityError, ProgrammingError
from zope.interface import implements
from zope.component import adapter, getUtility, queryUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope import schema
from zope.schema import getFields
from zope.schema.interfaces import IIterableSource, ICollection
from zope.event import notify
from PyQt4 import QtGui, QtCore
from pypapi.db.interfaces import IRelationResolver, IEntitiesRegistry, IListStore, IDatabase
from pypapi.db.storage import SAListStore, SingleItemStore, DifferentialStore
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.source import DbSource
from pypapi.db.field import DbObject
from pypapi.db.model.entities.base import EntitaBase
from pypapi.ui.cute.interfaces import IForm, IDataContext, IIndexChangedEvent, \
     IModel, IModelCursor, IColumn, ISelectForm, ISelectFormLite, IQuickInsertForm
from pypapi.ui.cute.event import IndexChangedEvent, ModelCursorChangedEvent, \
     local_event, provideHandler, CommitChangesEvent
from pypapi.ui.cute.model import StandardLookupModel, TableModel
from pypapi.ui.widgets.pickerentity import PickerEntity


logger = getLogger('cute')

class DataContext(QtCore.QObject):

    implements(IDataContext, IModelCursor)
    model = None
    mapper = None
    current_index = None
    current_entity = None
    parent_entity = None
    _lookup_model = None
    _selection_model = None # non un QTableModel, ma un QItemSelectionModel
    lookup_source = None
    _store = None

    def __init__(self, parent, root_int, name,  columns=None, factory=None):

        QtCore.QObject.__init__(self, parent)
        self.root_interface = root_int
        fields, interfaces = IRelationResolver(root_int).resolveRelations(name)
        if len(fields) > 0:
            field = fields.pop()
        else:
            field = None
        self.field = field

        self.interface = interfaces.pop()
        if len(interfaces) > 0:
            parent_interface = interfaces.pop()
            provideHandler(self.parentIndexChanged)
        else:
            parent_interface = None
        self.parent_interface = parent_interface
        self.name = name
        if columns is not None:
            model = self.createModel()
            self.model = model
            model.columns = columns
            model.factory = factory
            self.mapper = QtGui.QDataWidgetMapper(self)
            self.mapper.setModel(model)
            self.connect(self.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.indexChanged)
            if self.name == '.':
                primary_dc = self
            else:
                try:
                    primary_dc = getUtility(IDataContext, '.', parent)
                except ComponentLookupError:
                    primary_dc = None
            if primary_dc is not None:
                self.connect(self.model, QtCore.SIGNAL('dataChanged(const QModelIndex, const QModelIndex)'), primary_dc.modelDataChanged)
                self.connect(self.model, QtCore.SIGNAL('rowsRemoved(const QModelIndex, int, int)'), primary_dc.modelDataChanged)
                self.connect(self.model, QtCore.SIGNAL('rowsInserted(const QModelIndex, int, int)'), primary_dc.modelDataChanged)

    def modelDataChanged(self, i, j):
        if not self.is_dirty and self.current_entity is not None:
            if self.current_entity.readonly is False:
                self.editElement()
                notify(ModelCursorChangedEvent(self))
            else:
                self.cancelChanges()

    def indexChanged(self, row):

        cnt = self.model.rowCount()
        # Solo per il DC primario, implementa l'IModelCursor
        if self.name == '.':
            if cnt == 0:
                self.at_bof = True
                self.at_eof = True
            else:
                self.at_bof = (row < 1)
                self.at_eof = (row >= cnt-1)

        if cnt > 0:
            entity = self.model.getEntityByRow(row)
            event = IndexChangedEvent(self, entity, row)
            self.current_index = row
            self.current_entity = entity
            notify(event)
            logger.debug("Cambio indice sul modello '%s', indice %s", self.name, row)

    @adapter(IDataContext, IIndexChangedEvent)
    @local_event
    def parentIndexChanged(self, data_context, event):

        if data_context.interface is self.parent_interface and \
               self.name.startswith(data_context.name) and \
               self.name != data_context.name:
            bound_field = self.field.bind(event.entity)
            try:
                data = bound_field.get(event.entity)
            except AttributeError:
                data = None
            self.parent_entity = event.entity
            if self.model:
                if self.cardinality == 1:
                    data = SingleItemStore(bound_field)
                self.store = data
                #if len(self.store) > 0:
                self.mapper.toFirst()

    def _getStore(self):

        return self._store

    def _setStore(self, store):

        self._store = store
        self.model.store = store

    store = property(_getStore, _setStore)

    def _initSelectionModel(self):

        self._selection_model = sm = QtGui.QItemSelectionModel(self.model, self)
        self.connect(sm, QtCore.SIGNAL('currentRowChanged(QModelIndex,QModelIndex)'),
                                self.mapper, QtCore.SLOT('setCurrentModelIndex(QModelIndex)'))

    def _getSelectionModel(self):

        if self._selection_model is None and self.model is not None:
            self._initSelectionModel()
        return self._selection_model

    selection_model = property(_getSelectionModel)

    def getDetailDataContext(self, field):

        if isinstance(field, basestring):
            field = getFields(self.interface)[field]
        else:
            assert field in getFields(self.interface).values()
        if self.name == '.':
            sub_name = '.%s' % field.__name__
        else:
            sub_name = '%s.%s' % (self.name, field.__name__)
        sub_dc = queryUtility(IDataContext, sub_name, context=self)
        if sub_dc is None:
            form = getUtility(IForm, context=self)
            sub_dc = form.createDataContext(sub_name, no_lookups=True)
        return sub_dc

    def _initLookupModel(self):

        if self.field is not None:
            self.lookup_source = IIterableSource(self.field, None)
        l_model = self.createLookupModel()
        if self.lookup_source is not None:
            l_model.store = list(self.lookup_source)
        self._lookup_model = l_model

    def _getLookupModel(self):
        if self._lookup_model is None:
            self._initLookupModel()
        else:
            if self.parent_entity is not None:
                source = IIterableSource(self.field.bind(self.parent_entity))
                if source != self.lookup_source:
                    self.lookup_source = source
                    self._lookup_model.store = list(source)
                    self._lookup_model.reset()
        return self._lookup_model

    lookup_model = property(_getLookupModel)

    def createModel(self):

        model = getMultiAdapter((SAListStore(disable_session=True), self), IModel)
        return model

    def createLookupModel(self):

        model = StandardLookupModel(self.field, self)
        return model

    def _getCardinality(self):

        if (self.field is None) or ICollection.providedBy(self.field):
            return 2
        else:
            return 1

    cardinality = property(_getCardinality)


    ## IModelCursor

    _at_eof = False
    def _getEof(self):
        return self._at_eof
    def _setEof(self, at_eof):
        if self._at_eof != at_eof:
            self._at_eof = at_eof
            notify(ModelCursorChangedEvent(self))
    at_eof = property(_getEof, _setEof)

    _at_bof = False
    def _getBof(self):
        return self._at_bof
    def _setBof(self, at_bof):
        if self._at_bof != at_bof:
            self._at_bof = at_bof
            notify(ModelCursorChangedEvent(self))
    at_bof = property(_getBof, _setBof)

    _is_dirty = False
    def _getDirty(self):
        return self._is_dirty
    def _setDirty(self, is_dirty):
        if self._is_dirty != is_dirty:
            self._is_dirty = is_dirty
            if not is_dirty:
                self._is_new = False

            notify(ModelCursorChangedEvent(self))
    is_dirty = property(_getDirty, _setDirty)

    _is_new = False
    def _getNew(self):
        return self._is_new
    def _setNew(self, is_new):
        if self._is_new != is_new:
            self._is_new = is_new
            if is_new:
                self._is_dirty = True
            notify(ModelCursorChangedEvent(self))
    is_new = property(_getNew, _setNew)

    def firstElement(self):
        self.mapper.toFirst()

    def prevElement(self):
        self.mapper.toPrevious()

    def nextElement(self):
        self.mapper.toNext()

    def lastElement(self):
        self.mapper.toLast()

    def editElement(self):
        self.is_dirty = True

    def insertElement(self):
        self.model.insertRows(-1, 1)
        self.mapper.toLast()
        self.is_dirty = True

    def deleteElement(self):
        "Cancella l'elemento corrente, chiedendo conferma e mantenendo la posizione."

        confirm = QtGui.QMessageBox.question(None, u"Conferma cancellazione",
                                             u"Confermi l'eliminazione di questo elemento?",
                                             QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if confirm == QtGui.QMessageBox.Yes:
            ci = self.mapper.currentIndex()
            self.model.removeRows(ci, 1)
            if self._at_eof:
                self.mapper.toLast()
            else:
                self.mapper.setCurrentIndex(ci)
            self.flushChanges()

    def cancelChanges(self):
        session = object_session(self.current_entity)
        if session is not None:
            if self.current_entity in session.new:
                session.expunge(self.current_entity)
                # e poi cosa faccio??
            else:
                session.refresh(self.current_entity)
        self.mapper.revert()
        self.is_dirty = False
        event = IndexChangedEvent(self, self.current_entity, self.current_index)
        notify(event)
        logger.debug("Annullamento delle modifiche sul modello '%s', indice %s", self.name, self.current_index)

    def commitChanges(self):
        self.mapper.submit()
        self.is_dirty = False
        event = CommitChangesEvent(self)
        notify(event)

    def flushChanges(self):
        self.mapper.submit()
        self.is_dirty = False
        db = getUtility(IDatabase)
        res = db.flushSession(object_session(self.current_entity))
        if res is not True:
            error = res
            info = str(error)
            msg = error.args[0]
            title = 'Errore inserimento'
            msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                                       title,
                                       msg,
                                       QtGui.QMessageBox.Ok)
            msgbox.setDetailedText(info)
            msgbox.exec_()
        self.mapper.revert()
        event = CommitChangesEvent(self)
        notify(event)

    def search(self):
        "Mostra il dock per effettuare delle ricerche"
        win = self.parent()
        if hasattr(win, '_search_widget'):
            search_wgd = win._search_widget
            search_wgd.setVisible(True)
            if hasattr(search_wgd, 'criteria') and len(search_wgd.criteria.search_wdgs) == 0:
                search_wgd.executeSearch()

    def refresh(self):
        """
        Mette in expire l'elemento corrente, e notifica un cambio d'indice
        per forzare il caricamento dei dati.
        """
        session = object_session(self.current_entity)
        if session is not None and self.current_entity not in session.new:
            session.refresh(self.current_entity)
            self.is_dirty = False
        self.mapper.revert()
        event = IndexChangedEvent(self, self.current_entity, self.current_index)
        notify(event)
        logger.debug("Refresh sul modello '%s', indice %s", self.name, self.current_index)

    def selectFromId(self, path, search_id, differential=False, lite=False, null_item=False, colnames=None, **search_terms):

        try:
            pdc = getUtility(IDataContext, '.', self.parent())
            parent_session = object_session(pdc.current_entity)
        except ComponentLookupError:
            parent_session = None
        if parent_session is None:
            parent_session = getUtility(IDatabase).session

        path = path.strip()
        if len(path) == 0:
            path = self.name
        elif not path.startswith('.'):
            if self.name == '.':
                path = '.%s' % path
            else:
                path = '%s.%s' % (self.name, path)
        resolver = IRelationResolver(self.root_interface)
        resolver.bind(self)
        interface = resolver.resolveInterface(path)
        reg = getUtility(IEntitiesRegistry)
        klass = reg.getEntityClassFor(interface)
        source = DbSource(parent_session.query(klass))
        if search_terms and IDbSource.providedBy(source):
            source = source.filter(search_terms.items())
        try:
            if hasattr(source, 'query'):
                query = source.query
            else:
                query = source
            item = query.get(search_id)
            try:
                newitem = self.interface(item)
                self.model.insertRows(-1, 1, entities=[newitem,])
                return (newitem,)
            except TypeError:
                logger.debug("Fallito l'adattamento di %s a %s", item, self.interface)
        except InvalidRequestError:
            return self.selectFrom(path, differential=False, lite=False,
                                   null_item=False, colnames=False, **search_terms)


    def selectFrom(self, path, differential=False, lite=False, null_item=False, colnames=None, parent=QtCore.QModelIndex(), **search_terms):

        try:
            pdc = getUtility(IDataContext, '.', self.parent())
            parent_session = object_session(pdc.current_entity)
        except ComponentLookupError:
            parent_session = None
        if parent_session is None:
            parent_session = getUtility(IDatabase).session

        path = path.strip()
        if len(path) == 0:
            path = self.name
        elif not path.startswith('.'):
            if self.name == '.':
                path = '.%s' % path
            else:
                path = '%s.%s' % (self.name, path)
        if colnames is None:
            colnames = ('caption',)
        resolver = IRelationResolver(self.root_interface)
        resolver.bind(self)
        interface = resolver.resolveInterface(path)
        source = resolver.resolveSource(path)
        # accetto solo query
        if isinstance(source, DbSource) and parent_session == source.query.session:
            pass
        elif isinstance(source, Query):
            source = DbSource(source)
        else:
            reg = getUtility(IEntitiesRegistry)
            klass = reg.getEntityClassFor(interface)
            source = DbSource(parent_session.query(klass))
        limit = self.interface.get('limit').getTaggedValue('default')
        if limit > 0:
            source.limit = limit
        try:
            dialog = getUtility(ISelectForm, path, self.parent())
        except ComponentLookupError:
            if lite is not False:
                dialog = ISelectFormLite(source)
                rect = lite
                dialog.setGeometry(rect)
                dialog.setEntityToSelect(self.store.get())
                dialog.setNullItem(null_item)
            else:
                dialog = ISelectForm(source)
        parentForm = getUtility(IForm, '.')
        dialog.parent_form = parentForm
        dialog.setLimit(limit)
        # XXX: da ripristinare... (tolto con il multi sessione)
        #if differential is True:
        #    store = DifferentialStore(source, self.store)
        #    columns = [IColumn(interface.get(name)) for name in colnames]
        #    model = TableModel(store, columns=columns)
        #    model.editable = False
        #    dialog = ISelectForm(model)
        try:
            quick_insert = getUtility(IQuickInsertForm, path, self.parent())
            dialog.setQuickInsertForm(quick_insert)
        except ComponentLookupError:
            pass
        if hasattr(dialog, 'criteria') and len(dialog.criteria.search_wdgs) == 0:
            dialog.executeSearch()
        res = dialog.exec_()
        if res == dialog.Accepted:
            selection = dialog.selection
        else:
            selection = None
        if selection is not None:
            for item in selection:
                try:
                    if item is not None:
                        newitem = self.interface(item)
                    else:
                        newitem = None
                    self.model.insertRows(-1, 1, parent=parent, entities=[newitem,])
                except TypeError:
                    logger.debug("Fallito l'adattamento di %s a %s", item, self.interface)
                    selection = None
            self.model.reset()
        return selection


#    def getSearchFields(self, path):
#        resolver = IRelationResolver(self.root_interface)
#        resolver.bind(self)
#        interface = resolver.resolveInterface(path)
#        search_fields = []
#        for s in interface.names():
#            field = interface.get(s)
#            try:
#                if field.getTaggedValue('search') is True:
#                    qt_class, parser = SEARCH_WDGS[field.__class__]
#                    if isinstance(field, DbObject) or isinstance(field, schema.Choice):
#                        entity = field.getTaggedValue('entity')
#                    else:
#                        entity = None
#                    search_fields.append((s, field, qt_class, parser, entity))
#            except KeyError:
#                pass
#        return search_fields


# class DCAction(QAction):

#     def __init__(self, data_context):
