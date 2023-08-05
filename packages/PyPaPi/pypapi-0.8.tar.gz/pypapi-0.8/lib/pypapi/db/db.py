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
from zope.interface import implements, classImplements
from zope.component import provideUtility
from zope.event import notify
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import InvalidRequestError, InternalError, IntegrityError, ProgrammingError
from pypapi.db.interfaces import IDatabase, IDatabaseOpenedEvent, IDatabaseClosedEvent, \
     IDatabaseCreationEvent, IListStore

# inizializzazione supporto database
import pypapi.db.event
import pypapi.db.registry
import pypapi.db.factory
import pypapi.db.util
import pypapi.db.relation
import pypapi.db.satraverser
import pypapi.db.permission

# Dichiaro che l'InstrumentedList può essere usata come backend di
# storage
classImplements(InstrumentedList, IListStore)

logger = getLogger('db')

class DatabaseError(Exception):
    """Notifica errori avvenuti nel Database manager"""


class Database(object):
    """Gestisce il db a basso livello."""

    implements(IDatabase)

    # URI di connessione di default, usato dai test
    URI = 'postgresql://127.0.0.1/pypapi'

    def __init__(self, uri=None):

        self.uri = uri
        self.echo = False
        self._ready = False
        self._name = ''
        self._color = None

    def _getName(self):
        return self._name
    def _setName(self, name):
        self._name = name
    name = property(_getName, _setName)

    def _getColor(self):
        return self._color
    def _setColor(self, color):
        self._color = color
    color = property(_getColor, _setColor)

    def _getReady(self):

        return self._ready

    ready = property(_getReady)

    def _checkReadyness(self):

        if self._ready is False:
            raise DatabaseError("Database non pronto! Hai eseguito open()?")

    def _getEngine(self):

        self._checkReadyness()
        return self._engine

    engine = property(_getEngine)

    def createNewSession(self):
        "Crea e restituisce una nuona sessione"
        self._checkReadyness()
        new_session = create_session(bind=self._engine, autoflush=False)
        return new_session

    def _getSession(self):

        self._checkReadyness()
        return self._session

    session = property(_getSession)

    def open(self, uri=None):

        if self._ready:
            raise DatabaseError(u"Il database è già pronto")
        if not uri:
            uri = self.uri
        else:
            self.uri = uri
        if not uri:
            uri = self.URI
        if uri is None:
            raise DatabaseError(u"Devi fornire una stringa di connessione al database")
        self._engine = create_engine(uri, echo=self.echo)
        self._session = create_session(bind=self._engine, autoflush=False)
        self._ready = True
        notify(OpenEvent())

    def flushSession(self, session=None):

        if session is None:
            session = self.session
        error = None
        try:
            session.flush()
            session.expire_all()
        except (InternalError, IntegrityError, ProgrammingError), e:
            logger.error("Commit error: %s", e)
            return e
        return True


    def close(self, save=True):

        if not self._ready:
            return
        if save:
            self.session.flush()
        self.session.expunge_all()
        del self._session
        # l'engine non sembra avere un metodo appropriato per la
        # disconnessione
        del self._engine
        self._ready = False
        notify(CloseEvent())

class OpenEvent(object):
    implements(IDatabaseOpenedEvent)

class CloseEvent(object):
    implements(IDatabaseClosedEvent)

class CreationEvent(object):
    implements(IDatabaseCreationEvent)

def createDatabase(uri=None):
    database_utility = Database(uri=uri)
    provideUtility(database_utility, provides=IDatabase)
    notify(CreationEvent())
    return database_utility
