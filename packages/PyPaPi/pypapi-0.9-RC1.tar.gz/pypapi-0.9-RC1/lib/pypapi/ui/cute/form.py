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
from PyQt4 import QtGui, QtCore
from zope.interface import implements, classImplements, implementer
from zope.component import provideAdapter, getFactoryInterfaces, getMultiAdapter, \
     adapter, getUtility, getFactoriesFor, provideUtility, queryUtility
from zope.component.interfaces import IFactory
from zope.component.registry import Components
from zope.component.factory import Factory
from zope.schema import getFieldsInOrder, Bool
from zope.schema.interfaces import IChoice, IIterableSource
from zope.event import notify
from pypapi.db.interfaces import IListStore, IRelationResolver
from pypapi.ui.cute.interfaces import IForm, IStoreEditForm, IDataContext, IColumn
from pypapi.ui.cute.loader import loadUi
from pypapi.ui.cute.event import WidgetCreationEvent
from pypapi.ui.cute.datacontext import DataContext
from pypapi.ui.widgets.navigationbar import addStandardToolBars

# inizializzazione framework
import pypapi.db.event
import pypapi.db.relation
from  pypapi.db.storage import SAListStore

logger = getLogger('cute')

class BaseForm(Components):

    implements(IForm)
    _ui_loaded = False
    ui_filename = None

    def __init__(self, ui_filename=None):

        if ui_filename is not None:
            self.ui_filename = ui_filename
        self.initForm()

    def loadUi(self):

        if not self._ui_loaded:
            if self.ui_filename is None:
                self.autoLayout()
            else:
                loadUi(self.ui_filename, self)
            self._ui_loaded = True

    def handleNewWidget(self, widget):

        setattr(self, str(widget.objectName()), widget)

    def initForm(self):

        Components.__init__(self)
        self.registerUtility(self, IForm)

    def autoLayout(self):

        layout = self.layout()
        groupbox = QtGui.QGroupBox()
        glayout = QtGui.QGridLayout()
        groupbox.setLayout(glayout)
        layout.addWidget(groupbox)
        self.setCentralWidget(groupbox)
        names = self.interface.names()
        dc = IDataContext(self)
        mapper = dc.mapper
        for i in range(len(dc.model.columns)):
            column = dc.model.columns[i]
            name = column.name
            field = self.interface.get(name)
            glayout.addWidget(QtGui.QLabel(name), i, 0)
            if isinstance(field, Bool):
                widget = QtGui.QCheckBox()
            else:
                widget = QtGui.QLineEdit()
            widget.setObjectName(QtCore.QString(name))
            setattr(widget, 'column', QtCore.QString(name))
            glayout.addWidget(widget, i, 1)
            setattr(self, name, widget)
            mapper.addMapping(widget, i)



class StoreEditForm(BaseForm):

    implements(IStoreEditForm)
    columns = {}
    interface = None

    def __init__(self, store, interface=None, **kw):

        if interface is not None:
            self.interface = interface
        BaseForm.__init__(self, **kw)
        self.store = store

    def initForm(self):

        BaseForm.initForm(self)
        if self.columns:
            self.initModels()
            self.loadUi()
        elif self.interface is not None:
            self.createDataContext('.')
            self.loadUi()
        self.initToolBars()

    def initToolBars(self):
        """Aggiungi le toolbar standard.

        Se la form ha il concetto di toolbar, aggiungi le barre
        standard, in primis quella di navigazione.

        Le sottoclassi potranno fare l'override di questo metodo,
        per inserire barre diverse, o per customizzare i pulsanti
        della barra di navigazione, o ancora per non aggiungere
        alcuna barra.
        """

        if hasattr(self, 'addToolBar'):
            addStandardToolBars(self)

    def _setStore(self, store):

        primary_dc = getUtility(IDataContext, '.', self)
        primary_dc.store = store

    def _getStore(self):

        primary_dc = getUtility(IDataContext, '.', self)
        return primary_dc.store

    store = property(_getStore, _setStore)

    def edit(self, index):

        primary_dc = getUtility(IDataContext, '.', self)
        primary_dc.mapper.setCurrentIndex(index)

    def initModels(self):

        paths = self.columns.keys()
        paths.sort()
        for path in paths:
            self.createDataContext(path)

    def createDataContext(self, path, no_lookups=False):

        columns = None
        if path in self.columns:
            columns = self.columns[path]
            factory = self.factory[path]
        else:
            interface = IRelationResolver(self.interface).resolveInterface(path)
            factory_id = None
            factory = (factory_id, ((),{}))
            columns = [IColumn(field) for name, field in getFieldsInOrder(interface)]
            # in alcuni casi, crea il dc senza campi di lookup, in
            # modo da evitare che il calcolo del dc di lookup porti
            # alla creazione di dc troppo "profondi" che non servono
            # alla gestione della ui
            if no_lookups is True:
                columns = [c for c in columns if not IChoice.providedBy(c.context)]
        dc = DataContext(self, self.interface, path, columns, factory)
        self.registerUtility(dc, IDataContext, name=path)
        return dc

    def handleNewWidget(self, widget):

        BaseForm.handleNewWidget(self, widget)
        notify(WidgetCreationEvent(widget, self))


@adapter(IStoreEditForm)
@implementer(IDataContext)
def defaultStoreFormDC(store_form):

    primary_dc = getUtility(IDataContext, '.', store_form)
    return primary_dc

provideAdapter(defaultStoreFormDC)


class RegistrationError(Exception):
    pass


class StoreFormRegistration(object):

    def __init__(self, _class, root_interface, filename, name='', title=None,
                 form_interface=None, store_interface=None, primary=True, form_source=''):

        cdict = {}
        if filename == 'no':
            cdict['ui_filename'] = None
        else:
            cdict['ui_filename'] = self._path(filename)
        cdict['interface'] = root_interface
        for attr in ('columns','factory'):
            c_attr = getattr(_class, attr, None)
            if c_attr is None:
                cdict[attr] = {}
        if title is not None:
            cdict['title'] = title
        form_class = type(_class.__name__, (_class, StoreEditForm), cdict)
        store_interface = store_interface or IListStore
        if form_interface is not None:
            classImplements(form_class, form_interface)
        self.form_class = form_class
        # None nella riga sotto sta ad indicare il parent widget, che
        # però è opzionale
        if primary is True:
            provideAdapter(self.entityToForm, (self.form_class.interface,), IForm)

        if form_source == '' or form_source is None:
            form_source = name

        form_source = name

        self.form_source = form_source

        provideAdapter(self.storeToForm, (IListStore,), IForm, form_source)
        provideAdapter(self.storeAndParentToForm, (IListStore, None), IForm, form_source)
        provideAdapter(self.sourceToSearchForm, (IIterableSource,), IForm, form_source)

    def _path(self, filename):

        import sys, os
        try:
            upper_globals = sys._getframe(2).f_globals
        except ValueError:
            upper_globals = {}
        mod_file = upper_globals.get('__file__')
        if mod_file:
            return os.path.join(os.path.dirname(mod_file), filename)
        return filename

    def setModel(self, columns=None, name='.', factory_id=None, factory_args=((),{}), factory=None):

        root_int = getattr(self.form_class, 'interface', None)
        interface = IRelationResolver(root_int).resolveInterface(name)
        if factory_id:
            implemented = getFactoryInterfaces(factory_id)
            if interface not in implemented.interfaces:
                raise RegistrationError("Hai specificato una factory che non genera entità compatibili")
        elif factory is not None and not IFactory.implementedBy(factory):
            # suppongo che factory sia una classe e costruisco una factory al volo
            factory_id = '%s.%s' % (factory.__module__, factory.__name__)
            factory = Factory(factory, factory_id, factory.__class__.__doc__, \
                              (interface,))
            provideUtility(factory, IFactory, factory_id)
        else:
            factories = list(getFactoriesFor(interface))
            if len(factories) > 0:
                factory_id = factories[0][0]
                for fid in factories[1:]:
                    if fid[0].split('.')[-1] == interface.__name__:
                        factory_id = fid[0]
        if columns is None:
            # se non sono state passate delle colonne, costriusco
            # automaticamente una colonna per tutti i campi dell'
            # interfaccia
            columns = [IColumn(field) for field_name, field in getFieldsInOrder(interface)]
        self.form_class.columns[name] = columns
        self.form_class.factory[name] = (factory_id, factory_args)

    def entityToForm(self, entity):
        """Data un entità che implementa self.form_class.interface,
        restituisce una form appropriata per visualizzare, modificare
        tale entità."""
        store = IListStore(entity)
        form = self.form_class(store, None)
        notify(WidgetCreationEvent(form, form))
        return form

    def storeAndParentToForm(self, store, parent):
        """Dato uno store e un parent restituisce una form appropriata
        per visualizzare, modificare tale store"""
        form = self.form_class(store, parent)
        notify(WidgetCreationEvent(form, form))
        return form

    def storeToForm(self, store):
        "Dato uno store, restituisce una form"
        return self.storeAndParentToForm(store, None)

    def sourceToSearchForm(self, source):
        """Data una sorgente, restituisci una form di ricerca"""
        form = self.form_class(SAListStore(source), None)
        form.registerUtility(source)
        notify(WidgetCreationEvent(form, form))
        return form


def demo_BaseForm():

    from PyQt4 import QtGui, QtCore
    import os

    class TestDialog(QtGui.QDialog, BaseForm):

        ui_filename = os.path.join(os.path.dirname(__file__), 'test/baseform.ui')

        def __init__(self, *args):

            QtGui.QDialog.__init__(self, *args)
            BaseForm.__init__(self)
            self.loadUi()
            self.button1.setEnabled(False)

        @QtCore.pyqtSignature("")
        def on_button1_clicked(self):

            self.button1.setEnabled(False)
            self.button2.setEnabled(True)
            form = queryUtility(IForm, context=self.button2)
            print form

        @QtCore.pyqtSignature("")
        def on_button2_clicked(self):

            self.button1.setEnabled(True)
            self.button2.setEnabled(False)

    app = QtGui.QApplication([])
    dialog = TestDialog()
    dialog.show()
    app.exec_()


def demo_StoreEditForm():

    from PyQt4 import QtGui
    import zope.component.event
    from zope.schema import getFieldsInOrder
    from pypapi.db.interfaces import IIterProcedurale, IDatabase
    from pypapi.db.model import IterProcedurale
    from pypapi.ui.cute.interfaces import IColumn

    class TestDialog(QtGui.QDialog):

        def __init__(self, store, parent):

            QtGui.QDialog.__init__(self)
            self.initForm()
            self.store = store

    test_register = StoreFormRegistration(TestDialog,
                                          IIterProcedurale,
                                          'test/storeeditform.ui')
    test_register.setModel([IColumn(field) for name, field in
                            getFieldsInOrder(IIterProcedurale)][:-3])
    # inizializzazione database
    db = getUtility(IDatabase)
    db.open('sqlite:///procedimenti.sqlite')
    iter_proc = SAListStore(db.session.query(IterProcedurale))

    app = QtGui.QApplication([])
    dialog = getMultiAdapter((iter_proc, None), IForm)
    dialog.edit(0)
    dialog.show()
    app.exec_()


if __name__ == '__main__':
    demo_StoreEditForm()
