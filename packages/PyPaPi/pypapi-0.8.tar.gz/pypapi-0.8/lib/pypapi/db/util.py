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
from zope.interface import implementer
from zope.component import getUtilitiesFor, adapter, provideAdapter, provideHandler, \
     getUtility
from zope.schema.interfaces import IChoice, IIterableSource
from zope.schema import getFieldsInOrder
from pypapi.db.interfaces import IORM, IDatabaseOpenedEvent, IDatabase, IEntitiesRegistry, \
     IRelationResolver
from pypapi.db.source import DbSource
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.search import Search
from pypapi.db.search.interfaces import ISearch

logger = getLogger('root')

def initDbSources(session):
    """Inizializza le sorgenti definite in interfaces.py e quindi
    prima che la sessione S.A. sia effettivamente istanziata."""
    reg = getUtility(IEntitiesRegistry)
    interfaces = [res[1] for res in getUtilitiesFor(IORM)]
    for interface in interfaces:
        fields = getFieldsInOrder(interface)
        for name, f in fields:
            if IChoice.providedBy(f):
                source = IIterableSource(f)
                if IDbSource.providedBy(source):
                    resolver = IRelationResolver(interface)
                    try:
                        rel_interface = resolver.resolveInterface('.%s' % f.__name__)
                    except AttributeError, e:
                        logger.error('Impossibile risolvere l\'interfaccia che valorizza il campo %s' % name)
                        raise AttributeError, e
                    logger.debug('Richiedo la classe che implementa l\'interfaccia %s (valorizzazione campo %s)' % (rel_interface, name))
                    rel_class = reg.getEntityClassFor(rel_interface)
                    source._initDb(session.query(rel_class))

# XXX: obsoleto, ora la form inizializza la propria sessione
@adapter(IDatabaseOpenedEvent)
def initDbSourcesOnOpened(event):
    db = getUtility(IDatabase)
    initDbSources(db.session)
#provideHandler(initDbSourcesOnOpened)

@adapter(IORM)
@implementer(IDbSource)
def completeSourceForEntity(orm_interface):
    """Data l'interfaccia di una entità, restituisce una sorgente
    contenente tutti gli elementi disponibili."""
    reg = getUtility(IEntitiesRegistry)
    entity_class = reg.getEntityClassFor(orm_interface)
    query = getUtility(IDatabase).createNewSession().query(entity_class)
    return DbSource(query)

provideAdapter(completeSourceForEntity)

@adapter(IORM)
@implementer(ISearch)
def searchForEntity(orm_interface):
    """Data l'interfaccia di una entità, restituisce un'istanza di
    Search basata sul suo adattamento a sorgente."""
    source = IDbSource(orm_interface)
    return Search(source)

provideAdapter(searchForEntity)

