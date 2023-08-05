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
import os
from datetime import date, timedelta

from PyQt4 import QtCore, QtGui

from zope import schema
from zope.component import getUtility, adapter, getMultiAdapter
from zope.schema.interfaces import IIterableSource
from zope.event import notify

from pypapi.db.storage import SAListStore, SingleItemStore
from pypapi.db.field import DbObject
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.search.interfaces import ISearch
from pypapi.db.interfaces import IRelationResolver
from pypapi.ui.cute.form import BaseForm, StoreEditForm
from pypapi.ui.cute.interfaces import IForm, IIndexChangedEvent, IDataContext, IPickerEntityWidget, IColumn
from pypapi.ui.cute.event import local_event, provideHandler, WidgetCreationEvent
from pypapi.ui.cute.datacontext import DataContext
from pypapi.ui.widgets.pickerentity import PickerEntity

DIR = os.path.split(__file__)[0]
TERMS_UI = os.path.join(DIR, 'ui/search_terms.ui')
ACCEPTED = QtGui.QDialog.Accepted

logger = getLogger('cute')

SEARCH_WDGS = {schema.Int:(QtGui.QLineEdit, int),
               schema.ASCII:(QtGui.QLineEdit, str),
               schema.ASCIILine:(QtGui.QLineEdit, str),
               schema.TextLine:(QtGui.QLineEdit, unicode),
               schema.Text:(QtGui.QLineEdit, unicode),
               schema.Bool:(QtGui.QCheckBox, bool),
               schema.Datetime:(QtGui.QDateEdit, date),
               DbObject:(PickerEntity, None),
               schema.Choice:(QtGui.QComboBox, None),
               schema.List:(PickerEntity, None),
               }

TYPES_WITH_ENTITY = (DbObject, schema.List)

class CriteriaDialog(QtGui.QDialog, StoreEditForm):

    def __init__(self, source, parent=None):
        QtGui.QDialog.__init__(self, parent)
        BaseForm.__init__(self, TERMS_UI)
        self.loadUi()
        self.interface = source.item_interface
        self.search = ISearch(source)
        search_fields = self.getSearchFields()
        terms_keys = [t[0] for t in search_fields]
        layout = QtGui.QVBoxLayout()
        grid = self.grid = QtGui.QGridLayout()
        layout.addLayout(grid)
        layout.addStretch()
        self._terms_edits = []
        self.search_wdgs = {}
        self.terms_box.setLayout(layout)
        self._addTerms(search_fields)
        self._createDataContexts(source)


    def getSearchFields(self):

        sorted = []
        unsorted = []
        search_fields = []
        for s in self.interface.names():
            field = self.interface.get(s)
            try:
                if field.getTaggedValue('search') is True:
                    qt_class, parser = SEARCH_WDGS[field.__class__]
                    if True in [isinstance(field, t) for t in TYPES_WITH_ENTITY]:
                        entity = field.getTaggedValue('entity')
                    else:
                        entity = None
                    try:
                        selection_path = field.getTaggedValue('selection_path')
                    except: # XXX: come faccio a vedere che eccezione è??
                        selection_path = None
                    t = (s, field, qt_class, parser, entity, selection_path)
                    try:
                        order = field.getTaggedValue('order')
                        sorted.append((order,) + t)
                    except:
                        unsorted.append(t)
                    #search_fields.append((s, field, qt_class, parser, entity, selection_path))
            except KeyError:
                pass
        sorted.sort()
        sorted = [s[1:] for s in sorted]
        search_fields = tuple(sorted+unsorted)
        return search_fields


    def _createDataContexts(self, source):
        try:
            entity = source.query._entities[0].entities[0]()
        except AttributeError:
            # InstrumentedList
            entity = source.query[0].__class__()
        fields = [(t[0], t[1], t[5]) for t in self.getSearchFields()]
        fields.sort()
        resolver = IRelationResolver(self.interface)
        for path, field, selection_path in fields:
            if True in [isinstance(field, t) for t in TYPES_WITH_ENTITY]:
                dc = self.createDataContext('.%s' % path, no_lookups=True)
                interface = resolver.resolveInterface(path)
                if isinstance(field, schema.List):
                    # per la ricerca ho bisogno di un DbObject anche per gli schema.List
                    # e un attributo fittizio (_contains_) che mi rappresenta un'istanza di entità
                    # presente nella List
                    oldname = field.__name__
                    name = '%s_contains_%s' % (oldname, selection_path)
                    field = DbObject(title=field.title,
                                     description=field.description,)
                    field.__name__ = name
                    setattr(entity, name, None)
                    self.search_wdgs[name] = self.search_wdgs[oldname]
                    del self.search_wdgs[oldname]
                bound_field = field.bind(entity)
                data = SingleItemStore(bound_field)
                dc.store = data
            if isinstance(field, schema.Choice):
                dc = self.createDataContext('.%s' % path, no_lookups=True)
                self.registerUtility(dc, IDataContext, name='.%s' % path)
                self.search_wdgs[path][0][1].setModel(dc.lookup_model)


    def _addTerms(self, fields):

        g_layout = self.grid
        for i in range(len(fields)):
            name, field, qt_class, parser, entity, selection_path = fields[i]
            new_label = QtGui.QLabel(field.title)
            g_layout.addWidget(new_label, i, 0)
            if qt_class is QtGui.QDateEdit:
                h_layout = QtGui.QHBoxLayout()
                new_wdg = []
                for j in (0,1):
                    cb = QtGui.QCheckBox()
                    label = 'da data'[j:] # :)
                    cb.setToolTip(label)
                    new_wdg.append(cb)
                    h_layout.addWidget(cb, 0)
                    de = QtGui.QDateEdit()
                    de.setCalendarPopup(True)
                    de.setToolTip(label)
                    de.setEnabled(False)
                    de.setDate(QtCore.QDate(date.today()))
                    self.connect(cb, QtCore.SIGNAL('toggled(bool)'), de, QtCore.SLOT('setEnabled(bool)'))
                    new_wdg.append(de)
                    h_layout.addWidget(de, 2)
                new_wdg[2].setEnabled(False)
                self.connect(new_wdg[0], QtCore.SIGNAL('toggled(bool)'), new_wdg[2], QtCore.SLOT('setEnabled(bool)'))
                g_layout.addLayout(h_layout, i, 1)
            elif qt_class is QtGui.QComboBox:
                h_layout = QtGui.QHBoxLayout()
                new_wdg = []
                cb = QtGui.QCheckBox()
                cb.setToolTip('abilita filtro')
                h_layout.addWidget(cb, 0)
                new_wdg.append(cb)
                combo = QtGui.QComboBox()
                combo.setEnabled(False)
                setattr(combo, 'column', QtCore.QString(name))
                h_layout.addWidget(combo, 2)
                new_wdg.append(combo)
                self.connect(cb, QtCore.SIGNAL('toggled(bool)'), combo, QtCore.SLOT('setEnabled(bool)'))
                g_layout.addLayout(h_layout, i, 1)
            else:
                new_wdg = qt_class()
                new_wdg.setToolTip(field.description)
                g_layout.addWidget(new_wdg, i, 1)
            if IPickerEntityWidget.implementedBy(qt_class):
                setattr(new_wdg, 'entity', QtCore.QString(entity))
                if selection_path is not None:
                    setattr(new_wdg, 'selection_path', selection_path)
                setattr(new_wdg, 'column', QtCore.QString('caption'))
            self.search_wdgs[name] = (new_wdg, parser)


    def executeSearch(self):
        # per ora filtro direttamente sulla source,
        # in futuro si può pensare di portare la funzionalità
        # del filter nel search
        source = self.search.source
        search_terms = {}
        for name, (wdg, parser) in self.search_wdgs.items():
            if isinstance(wdg, QtGui.QLineEdit):
                value = wdg.text()
                value = value.replace('*', '%')
                try:
                    value = parser(value)
                except ValueError:
                    value = None
            elif isinstance(wdg, QtGui.QCheckBox):
                value = wdg.checkState()
                value = parser(value)
            elif isinstance(wdg, list) and isinstance(wdg[1], QtGui.QDateEdit):
                check1, date1, check2, date2 = wdg
                d1 = check1.checkState() == QtCore.Qt.Checked and date1.date() or None
                d2 = check2.checkState() == QtCore.Qt.Checked and date2.date() or None
                if d1 is not None:
                    d1 = parser(d1.year(), d1.month(), d1.day())
                    if d2 is None:
                        d2 = d1 + timedelta(1)
                    else:
                        d2 = parser(d2.year(), d2.month(), d2.day())
                if d1 is not None:
                    value = [d1, d2]
                else:
                    value = None
            elif isinstance(wdg, PickerEntity):
                if len(str(wdg.text).strip()) > 0:
                    dc = IDataContext(wdg)
                    value = dc.store[0]
                else:
                    value = None
            elif isinstance(wdg, list) and isinstance(wdg[1], QtGui.QComboBox):
                if wdg[1].isEnabled():
                    dc = getUtility(IDataContext, '.%s' % name, self)
                    value = dc.lookup_model.store[wdg[1].currentIndex()]
                else:
                    value = None
            if value:
                search_terms[name] = value

        if len(search_terms.items()) > 0:
            source = source.filter(search_terms.items())
            return source
        elif len(self.search_wdgs.items()) > 0:
            msg = "E' necessario impostare almeno un filtro di ricerca"
            QtGui.QMessageBox.warning(self, 'Filtro richiesto', msg, QtGui.QMessageBox.Ok)
            return None
        return source


def createSearchWindow(source, parent=None):

    from pypapi.ui.widgets.pickerdialog import PickerDialog
    interface = source.getItemInterface()
    pd = PickerDialog(allow_multi=False,
                      source=source,
                      interface=interface)
    #pd.setParent(parent)
    return pd

def createDockFrame(widget, title, parent=None):
    features = QtGui.QDockWidget.NoDockWidgetFeatures | \
               QtGui.QDockWidget.DockWidgetVerticalTitleBar
    dock = QtGui.QDockWidget(title, parent)
    dock.setFeatures(features)
    dock.setWidget(widget)
    return dock


def addSearchHelperFor(form, instance=None):
    if hasattr(form, '_search_widget'): return
    if instance is None:
        source = form.queryUtility(IDbSource)
        if not source:
            source = IIterableSource(form.interface)
        limit = form.interface.get('limit').getTaggedValue('default')
        if limit > 0:
            source.limit = limit
        instance = createSearchWindow(source, form)
    instance.form = form
    form._search_widget = instance

def searchWindowModalPreview(source, form_name):

    search_form = createSearchWindow(source)
    search_form.setWindowModality(QtCore.Qt.WindowModal)
    notify(WidgetCreationEvent(search_form, search_form))
    res = search_form.exec_()
    if res == search_form.Accepted:
        selection = search_form.selection
        form = getMultiAdapter((source,), IForm, form_name)
        form.store = SAListStore(selection)
        return form

