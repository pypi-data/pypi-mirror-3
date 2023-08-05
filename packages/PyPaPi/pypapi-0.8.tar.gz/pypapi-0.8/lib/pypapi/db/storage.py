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
from sqlalchemy.orm import object_session
from zope.interface import classImplements, implements, implementer
from zope.interface import Interface
from zope.component import getUtility, provideAdapter, provideUtility, \
     queryUtility, adapts, adapter, provideHandler
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.schema.interfaces import IIterableSource
from pypapi.db.interfaces import IListStore, IDatabase, IORM, \
     IObjectAddedEvent, IObjectRemovedEvent, IEntitaBase

# anche la normale lista supporta tale interfaccia
classImplements(list, IListStore)

logger = getLogger('storage')

class SAListStore(list):
    """Adatta una IIterableSource ad un IListStore, usato per le
    Query SA"""

    # Per ora l'implementazione è molto semplice e forse,
    # incompleta. É inoltre evidente che molte delle potenzialità
    # della Query non vengono prese in considerazione. A questo
    # livello funzionale, solo la lazyness e il sorting sembrano
    # pertinenti.

    implements(IListStore)
    adapts(IIterableSource)

    def __init__(self, iter_source=None, disable_session=False):

        if iter_source is None:
            super(SAListStore, self).__init__()
        else:
            super(SAListStore, self).__init__(iter_source)
        self.context = iter_source
        self._session_is_disabled = disable_session

    def _delete(self, index):

        item = self[index]
        notify(ObjectRemovedEvent(self, item, index))
        session = object_session(item)
        if not self._session_is_disabled:
            logger.debug('Deleting %s', item)
            session.delete(item)

    def _save(self, item, index):

        # XXX do per scontato che l'oggetto da salvare non sia già
        # nella sessione
        notify(ObjectAddedEvent(self, item, index))
        session = getUtility(IDatabase).session
        if not self._session_is_disabled:
            logger.debug('Adding %s', item)
            session.add(item)

    def __setitem__(self, index, item):

        self._delete(index)
        self._save(item, index)
        super(SAListStore, self).__setitem__(index, item)

    def __delitem__(self, index):

        self._delete(index)
        super(SAListStore, self).__delitem__(index)

    def append(self, item):

        self._save(item, -1)
        super(SAListStore, self).append(item)

    def pop(self, index=-1):

        self._delete(index)
        return super(SAListStore, self).pop(index)

    def remove(self, index):

        self._delete(index)
        super(SAListStore, self).remove(index)

    def insert(self, index, item):

        self._save(item, index)
        super(SAListStore, self).insert(index, item)

@adapter(Interface)
@implementer(IListStore)
def storeForInterface(obj):

    assert Interface.providedBy(obj)
    return [obj]

@adapter(IEntitaBase)
@implementer(IListStore)
def storeForEntitaBase(entity):

    assert IEntitaBase.providedBy(entity)
    return SAListStore([entity])

provideAdapter(storeForInterface)
provideAdapter(storeForEntitaBase)

class DifferentialStore(SAListStore):

    def __init__(self, super_iterable, sub_store):

        diff = iter(i for i in super_iterable if i not in sub_store)
        super(DifferentialStore, self).__init__(diff, disable_session=True)
        self._sub_store = sub_store
        provideHandler(self._sub_add)
        provideHandler(self._sub_del)

    @adapter(IListStore, IObjectAddedEvent)
    def _sub_add(self, store, event):
        if store is self._sub_store:
            self.remove(self.index(event.item))

    @adapter(IListStore, IObjectRemovedEvent)
    def _sub_del(self, store, event):
        if store is self._sub_store:
            # l'append di seguito è un ovvia semplificazione
            self.append(event.item)


class SingleItemStore(object):

    implements(IListStore)

    def __init__(self, bound_field, fake_none=True):

        self.context = bound_field
        self.fake_none = fake_none

    def get(self):

        obj = self.context.context
        value = self.context.get(obj)
        return value

    def set(self, value):

        obj = self.context.context
        self.context.set(obj, value)

    def reset(self):

        self.set(None)

    def _checkIndex(self, index, error='list index out of bounds'):
        # XXX: il DataContext.selectFrom usato dal PickerEntity
        # inserisce in ultima posizione (in questo caso può essere 1)
        if index != 0 and index != 1:
            raise IndexError(error)
        value = self.get()
        if not self.fake_none:
            if value is None:
                raise IndexError(error)

    ## list protocol

    def append(self, item):

        self.set(item)

    def pop(self):

        value = self.get()
        if value is None:
            raise IndexError('pop from empty list')
        self.reset()
        return value

    def remove(self, index):

        self._checkIndex(index)
        self.reset()

    def insert(self, index, item):

        self._checkIndex(index)
        self.set(item)

    def __setitem__(self, index, item):

        self._checkIndex(index)
        self.set(item)

    def __delitem__(self, index):

        self._checkIndex(index)
        self.reset()

    def __getitem__(self, index):

        self._checkIndex(index)
        return self.get()

    def __len__(self):

        value = self.get()
        if (self.fake_none is True) or (value is not None):
            return 1
        return 0

    def __iter__(self):

        value = self.get()
        if (self.fake_none is True) or (value is not None):
            yield value
        return

    def __contains__(self, item):

        return self.get() is item

class StoreObjectEvent(ObjectEvent):

    def __init__(self, store, item,  index):

        super(StoreObjectEvent, self).__init__(store)
        self.item = item
        self.index = index


class ObjectAddedEvent(StoreObjectEvent):

    implements(IObjectAddedEvent)


class ObjectRemovedEvent(StoreObjectEvent):

    implements(IObjectRemovedEvent)


ORM_INTERFACE_ATTR = '__pypapi_orm_interface__'

def registerStore(store_inst, orm_interface):
    """Registra uno store legandolo ad una specifica interfaccia
    implementata da un'entità."""
    assert IListStore.providedBy(store_inst)
    assert IORM.providedBy(orm_interface)
    provideUtility(store_inst, IListStore,  '%s.%s' % (orm_interface.__module__, orm_interface.__name__))
    setattr(store_inst, ORM_INTERFACE_ATTR, orm_interface)

def queryStore(orm_interface):
    """Cerca uno store registrato per una determinata interfaccia,
    restituisce None se non lo trova"""

    name = '%s.%s' % (orm_interface.__module__, orm_interface.__name__)
    return queryUtility(IListStore, name)

def getORMInterfaceFor(store_inst):
    """Restituisce l'interfaccia delle entità per le quali questo
    store è stato registrato."""
    assert IListStore.providedBy(store_inst)
    i = getattr(store_inst, ORM_INTERFACE_ATTR, None)
    if i is None:
        raise ValueError, 'Questo store non è stato registrato'
    return i

def _isStored(utente):

    key = utente.id_utente
    from pypapi.db.model.entities import Utente
    db = getUtility(IDatabase)
    u = db.session.query(Utente).get(key)
    return (u is not None) and (u is utente)

def test_SAListStore():

    db = getUtility(IDatabase)
    db.echo = True
    db.open('sqlite:///procedimenti.sqlite')
    from pypapi.db.model.entities import Utente
    utenti = db.session.query(Utente)
    u_store = SAListStore(utenti)
    pinco = Utente()
    pinco.id_utente = u'pinco'
    pinco.cod_utente = 99
    # append
    u_store.append(pinco)
    db.session.flush()
    # delitem
    del u_store[-1]
    db.session.flush()
    assert not _isStored(pinco)
    db.close()

def test_storeRegistration():

    from pypapi.db.interfaces import IUtente
    store = SAListStore()
    registerStore(store, IUtente)
    utility = queryStore(IUtente)
    assert utility is store
    i = getORMInterfaceFor(utility)
    assert i is IUtente
