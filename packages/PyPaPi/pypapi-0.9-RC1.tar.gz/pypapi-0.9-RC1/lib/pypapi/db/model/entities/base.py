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


import logging
from datetime import datetime, date
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import object_mapper, object_session
from sqlalchemy.schema import DefaultClause

from zope.interface import implementedBy, implements
import zope.schema

from pypapi.db.interfaces import IEntitaBase


logger = logging.getLogger('model')

def trim(c, maxlength=100, ellipsis='...', omissis=None):
    "Tronca un stringa a una lunghezza massima, inserendovi degli omissis"

    if c is None:
        c = ''
    if c and maxlength:
        if omissis:
            if (len(c)-len(omissis)) > maxlength:
                halflen = maxlength//2
                c = c[:halflen] + omissis + c[-halflen:]
        else:
            if (len(c)-len(ellipsis)) > maxlength:
                c = c[:maxlength] + ellipsis
    return c


class EntitaBase(object):
    """Base astratta per tutte le entità"""

    implements(IEntitaBase)

    def __init__(self, **kwargs):
        """Inizializza una nuova istanza di questa classe.

        È possibile specificare un numero arbitrario di *keyword
        arguments*, che verranno usati per impostare il valore
        dell'attributo omonimo.  Se l'attributo non esiste (cioè, la
        tabella mappata a questa classe non ha un campo non quel nome,
        e neppure il mapper definisce una proprietà omonima), viene
        alzato un ``AttributeError``.
        """

        def isproperty(m,p):
            try:
                m.get_property(p)
                return True
            except InvalidRequestError:
                return False

        mapper = object_mapper(self)
        table = mapper.mapped_table
        columns = table.c
        for key in kwargs:
            if key in columns or isproperty(mapper, key):
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError("Uno dei parametri (%s) non corrisponde ad alcuna "
                                     "colonna nella tabella %r" % (key, table.name))

        if self.session is None:
            # non proviene da session.query, quindi è nuovo
            self.initNew()

    def __str__(self):
        """Ritorna una stringa che descrive questa istanza.

        Tipicamente le entità hanno un campo "descrizione", nel qual caso
        viene ritornato quello. Negli altri casi viene ritornato ``repr(self)``.
        Le sottoclassi potranno specializzare il metodo per ritornare
        l'informazione più consona.
        """

        try:
            if self.descrizione is not None:
                return self.descrizione
            else:
                return repr(self)
        except AttributeError:
            return repr(self)

    def __repr__(self):
        """Costruisci una rappresentazione testuale di questa istanza.

        La stringa viene costruita aggiungendo al nome della classe la lista
        di tutte le colonne della tabella mappata col loro rispettivo valore,
        separate da virgole e racchiuse tra parentesi tonde.
        """

        atts = []
        columns = object_mapper(self).mapped_table.c
        for column in columns:
            key = column.key
            if hasattr(self, key):
                col = columns.get(key)
                if not (getattr(col, 'server_default', None) is not None or
                        isinstance(getattr(col, 'default', None), DefaultClause) or
                        getattr(self, key) is None):
                    atts.append( (key, getattr(self, key)) )
        return ''.join([self.__class__.__name__, '(',
                        trim(', '.join([x[0] + '=' + repr(x[1]) for x in atts]),
                             maxlength=50, omissis='...'),
                        ')'])

    def __int__(self):
        """Ritorna la chiave primaria dell'entità."""

        pkey = [c for c in object_mapper(self).mapped_table.columns if c.primary_key]
        if len(pkey)==1:
            return getattr(self, pkey[0].key)
        else:
            raise InvalidRequestError('Class %s does not have a single-integer primary key',
                                      self.__class__.__name__)

    def __setattr__(self, name, value):
        """Esegui la validazione del valore verso tutte le interfacce implementate.

        Prima di assegnare il valore all'attributo, viene eseguito il `.validate()`
        su ciascuna interfaccia implementata dalla classe.
        """

        for i in implementedBy(self.__class__):
            field = i.get(name)
            if field is not None:
                # XXX: da sistemare...
                if isinstance(value, date):
                    value = datetime(value.year, value.month, value.day)
                if not (isinstance(field, (zope.schema.Choice, zope.schema.List,
                                           zope.schema.Object))):
                    bound = field.bind(self)
                    try:
                        bound.validate(value)
                    except Exception, e:
                        logger.warning("Can't assign value %r to %r: %s",
                                       value, name, e.__class__.__name__)
                        raise
        object.__setattr__(self, name, value)

    ## IEntitaBase

    def getCaption(self):
        """Metodo di generazione della proprietà caption.

        È buona norma che tale metodo sia ridefinito nelle classi figlie,
        che di default usa semplicemente `str()`.
        """

        return self.trimCaption(str(self))

    # Lunghezza ragionevole utilizzata per troncare la caption
    CAPTION_TRIM_LENGTH = 100
    CAPTION_TRIM_CHAR = '...' # u'\u2026'

    def trimCaption(self, c, maxlength=None, ellipsis=None):
        """Tronca la caption se supera `maxlength` caratteri."""

        return trim(c, maxlength or self.CAPTION_TRIM_LENGTH,
                    ellipsis or self.CAPTION_TRIM_CHAR)

    caption = property(lambda self: self.getCaption())

    ## Utility, primariamente per agevolare il test

    def updateFromDictionary(self, data, mapper=None):
        """
        Aggiorna l'istanza con i dati contenuti in un dizionario,
        fatto di valori, liste o altri dizionari.
        """

        updateFromDictionary(self, data, mapper)

    def getReadOnly(self):
        return False
    readonly = property(lambda self: self.getReadOnly())

    def getObjectSession(self):
        """
        Restituisce la sessione a cui è agganciato l'oggetto
        """
        return object_session(self)
    session = property(getObjectSession)

    def getIsNew(self):
        """
        L'oggetto deve ancora essere reso persistente nel database?
        """
        if self.session is None:
            return True
        return self in self.session.new
    is_new = property(getIsNew)

    def initNew(self):
        """
        """
        pass


# Variazione su UsageRecipes/ProcHash/prochash.py sul wiki SQLAlchemy

def updateFromDictionary(obj, data, mapper=None):
    """Update a mapped class with data from a Python nested hash/list structure.

    The `data` dictionary may contain either single scalar attributes, like
    ``progressivo = 1``, single dictionary representing a related entity,
    or lists of dictionaries for the one-to-many relations.

    A single entity is represented by a single dictionary: if it contains just
    the primary key, the entity is looked up in the database, otherwise a new
    entity is forged and updated with the items in the dictionary.

    Example::

        iterp.updateFromDictionary(dict(
            # A scalar value
            descrizione=u"Esempio di iter procedurale",
            # A foreign key entity, looked up by primary key
            contesto = dict(idcontesto="ANAG"),
            # A list of entities for a one-to-many relation: each entity
            # in the list has a sub-entity, the first is created new as
            # there is no primary key, while the second gets loaded from
            # the database, looked up by its primary key.
            fasiiterprocedurale = [dict(progressivo=1, fase=dict(descrizione=u"Fase estemporanea")),
                                   dict(progressivo=2, fase=dict(idfase=1))],
            ))
    """

    from sqlalchemy.orm.properties import PropertyLoader

    if not mapper:
        mapper = object_mapper(obj)
    session = object_session(obj)

    for col in mapper.mapped_table.c:
        key = col.key
        if data.has_key(key):
            setattr(obj, key, data[key])

    xx = [(a,b) for a,b in getattr(mapper, '_Mapper__props').items()
          if isinstance(b, PropertyLoader)]
    for rname,rel in xx:
        if data.has_key(rname) and data[rname] is not None:
            pkey = [c for c in rel.mapper.mapped_table.columns if c.primary_key]
            value = data[rname]
            if isinstance(value, dict):
                pkvalue = [value[c.key] for c in pkey if c.key in value]
                # if its just the primary key, load it
                if len(pkey)==len(value)==len(pkvalue):
                    subobj = session.query(rel.mapper.class_).get(*pkvalue)
                    setattr(obj, rname, subobj)
                else:
                    subobj = rel.mapper.class_()
                    setattr(obj, rname, subobj)
                    updateFromDictionary(subobj, value, rel.mapper)
            else:
                dbdata = getattr(obj, rname)
                for row in value:
                    pkvalue = [row[c.key] for c in pkey if c.key in row]
                    # if its just the primary key, load it
                    if len(pkey)==len(row)==len(pkvalue):
                        subobj = session.query(rel.mapper.class_).get(pkvalue)
                        dbdata.append(subobj)
                    else:
                        subobj = rel.mapper.class_()
                        dbdata.append(subobj)
                        updateFromDictionary(subobj, row, rel.mapper)
