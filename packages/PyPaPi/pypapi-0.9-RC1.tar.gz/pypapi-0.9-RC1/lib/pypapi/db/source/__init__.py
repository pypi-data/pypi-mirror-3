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

from sqlalchemy.orm import object_mapper, class_mapper
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.orderinglist import OrderingList

from zope.interface import classImplements, implements, implementer
from zope.component import getUtility, provideAdapter, adapter
from zope.schema.interfaces import IIterableSource, IChoice, \
     IContextSourceBinder

from pypapi.db.source.interfaces import IDbSource

# Specifico che la classe SA Query normalmente usata attraverso
# 'session.query' implementa l'interfaccia IIterableSource
classImplements(Query, IIterableSource)
classImplements(InstrumentedList, IIterableSource)

# Idem per la OrderingList
classImplements(OrderingList, IIterableSource)

logger = getLogger('source')


class DbSource(object):

    implements(IDbSource)

    def __init__(self, query=None, refresh_on_iter=True, **specs):

        self._limit = None
        self.query = query
        self.specs = specs
        if query is not None:
            self._initDb(query)
        self._auto_refresh = refresh_on_iter

    def _initDb(self, query):
        """Metodo utilizzato per l'inizializzazione ulteriore che va
        fatta al setup del database. Vedi
        pypapi.db.util.initDbSources."""

        if self.query is None:
            self.query = query.filter_by(**self.specs)

    def __contains__(self, value):

        return value in self.query

    def __iter__(self):

        if self._auto_refresh:
            self.refresh()
        return iter(self.query)

    def refresh(self):

        if isinstance(self.query, Query) and self.query is not None:
            self.query = self.query._clone()
        else:
            # come eseguire il refresh della InstrumentedList?
            pass

    def getItemInterface(self):

        from pypapi.db.interfaces import IEntitiesRegistry
        reg = getUtility(IEntitiesRegistry)
        if isinstance(self.query, Query):
            try:
                class_ = self.query.mapper.class_
            except AttributeError:
                # XXX: SA 0.5
                class_ = self.query._entities[0].entities[0]
                from pypapi.db.model.entities.base import EntitaBase
                assert issubclass(class_, EntitaBase)
        else:
            class_ = self.query[0].__class__
        interface = reg.getInterfaceFor(class_)
        return interface

    item_interface = property(getItemInterface)

    def getLimit(self):
        return self._limit

    def setLimit(self, limit):
        self._limit = limit

    limit = property(getLimit, setLimit)

    def filter(self, specs):

        try:
            mapper = self.query.mapper
        except AttributeError:
            # XXX: SA 0.5
            mapper = class_mapper(self.query._entities[0].entities[0])
        query = self.query
        for key, value in specs:
            contains = False
            contains_item = None
            try:
                c = mapper.columns[key]
            except KeyError:
                if 'contains' in key.split('_'):
                    contains_item = key[key.index('_contains')+10:]
                    key = key[:key.index('_contains')]
                    contains = True
                c = getattr(self.query._entities[0].entities[0], key)
            if isinstance(value, basestring):
                if not value[-1] == '%%':
                    value += '%%'
                value = unicode(value)
                import string
                alphadigits = string.letters + string.digits
                if value[0] in alphadigits + '%':
                    if value.find('%') > -1:
                        filter_spec = c.ilike(value)
                    else:
                        filter_spec = c == value
                else:
                    filter_spec = eval('c ' + value)
            elif isinstance(value, list) and len(value) == 2:
                filter_spec = c.between(value[0], value[1])
            else:
                if contains:
                    filter_spec = None
                    kw = {contains_item:getattr(value, contains_item),}
                    query = query.join(value.__class__).filter_by(**kw)
                    logger.debug("Filter 'item in list': %s", '%s in %s' % (contains_item, key))
                else:
                    filter_spec = c == value
            if filter_spec is not None:
                logger.debug("Filter spec: %s", filter_spec)
                query = query.filter(filter_spec)
        if self._limit is not None:
            query=query.limit(self._limit)
        return self.__class__(query=query)


@adapter(IChoice)
@implementer(IIterableSource)
def sourceForChoice(field):

    source = field.source
#    if not IIterableSource.providedBy(source):
#        raise ValueError("Il campo deve essere associato ad un'istanza per avere la sorgente")
    return source

provideAdapter(sourceForChoice)

class GenericSource(object):
    """Sorgente generica da utilizzare nel caso di elementi che non
    appartengono ad un set persistito con SA. Per essere compatibile
    con la libreria pypapi.ui.cute, allo stato attuale
    'source_factory' deve restituire una IIterableSource i cui
    elementi supportano l'interfaccia IEntitaBase."""

    implements(IContextSourceBinder)

    def __init__(self, source_factory, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs
        self.source_factory = source_factory

    def __iter__(self):

        return iter([])

    def __call__(self, context):

        if isinstance(self.source_factory, basestring):
            # se source_factory è una stringa, viene valutato in
            # questo contesto per ottenere il metodo o la funzione che
            # restituirà i valori della sorgente
            source_factory = eval(self.source_factory)
            if callable(source_factory):
                return source_factory(*self.args, **self.kwargs)
            else:
                return source_factory
        else:
            source_factory = self.source_factory
            return source_factory(context, *self.args, **self.kwargs)


class TestClass:

    def setUp(self):
        from pypapi.db.interfaces import IDatabase
        db = getUtility(IDatabase)
        db.open('sqlite:///procedimenti.sqlite')
        self.db = db

    def tearDown(self):

        self.db.close()

    def test_ChoiceSource(self):

        from pypapi.db.interfaces import IIterProcedurale
        from pypapi.db.model import entities
        db = self.db
        ip = db.session.query(entities.IterProcedurale).get(91)
        ente = IIterProcedurale.get('ente').bind(ip)
        assert ente.source[0].__class__ is entities.ElementoAnagrafico
        assert ente.source.count() == db.session.query(entities.ElementoAnagrafico).filter_by(tipo_anag='E').count()

    def test_ListSource(self):

        from pypapi.db.interfaces import IIterProcedurale
        from pypapi.db.model import entities
        db = self.db
        ip = db.session.query(entities.IterProcedurale).get(91)
        personereferenti = IIterProcedurale.get('personereferenti').bind(ip)
        assert personereferenti.value_type.source[0].__class__ is entities.Utente
        assert personereferenti.value_type.source.count() == db.session.query(entities.Utente).count()
