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


from types import MethodType
from logging import getLogger
from zope.interface import implements
from zope.component import provideHandler as baseProvideHandler, getSiteManager
from zope.component.interfaces import IObjectEvent, ObjectEvent, \
     IComponentLookup
from PyQt4 import QtCore
from pypapi.ui.cute.interfaces import IWidgetCreationEvent, \
     IIndexChangedEvent, IModelCursorChangedEvent, ICommitChangesEvent

logger = getLogger('cute')

def filterEventContext(func):
    """Filtra l'handling di un evento che implementa IObjectEvent
    eseguendo la func decorata solo se il registro locale dei
    componenti del soggetto dell'evento e del destinatario è il
    medesimo. Tradotto in pseudocodice:

      if IComponentLookup(event.object) is IComponentLookup(receiver):
          func(object, event)

    func deve essere un metodo."""
    def wrapper(receiver, *args, **kwargs):
        is_event_call = False
        event = None
        if len(args) > 0:
            for arg in args:
                if IObjectEvent.providedBy(arg):
                    is_event_call = True
                    event = arg
                    break
        if is_event_call:
            error = False
            try:
                sc = IComponentLookup(event.object)
            except RuntimeError:
                error = True
                import sys, gc
                rc = sys.getrefcount(event.object)
                logger.exception("Errore, il refcount dell'oggetto '%s' è %d",
                                 event.object, rc)
                gc.collect()
                logger.debug("Referents: '%s'", gc.get_referents(event.object))
                logger.debug("Referrers: '%s'", gc.get_referrers(event.object))
            try:
                rc = IComponentLookup(receiver)
            except RuntimeError:
                error = True
                import sys, gc
                rc = sys.getrefcount(receiver)
                logger.exception("Errore, il refcount dell'oggetto '%s' è %d",
                                 receiver, rc)
                logger.debug("Referents: '%s'", gc.get_referents(receiver))
                logger.debug("Referrers: '%s'", gc.get_referrers(receiver))
            if not error and (sc is rc):
                func(receiver, *args, **kwargs)
        else:
            func(receiver, *args, **kwargs)
    return wrapper

local_event = filterEventContext

def provideHandler(factory, adapts=None):
    """Versione modificata di zope.component.provideHandler che
    installa uno slot per rimuovere la registrazione dell'handler alla
    distruzione dell'istanza di cui fa parte... ovviamente, nel caso
    si tratti di un metodo."""
    baseProvideHandler(factory, adapts)
    if isinstance(factory, MethodType):
         def removeEventHandler(ignored):
             sm = getSiteManager()
             sm.unregisterHandler(factory)
         QtCore.QObject.connect(factory.im_self, QtCore.SIGNAL("destroyed(QObject *)"), removeEventHandler)

class WidgetCreationEvent(ObjectEvent):
    """Evento che segnala l'avvenuta creazione di un nuovo widget"""

    implements(IWidgetCreationEvent)

    def __init__(self, object, tlw):

        super(WidgetCreationEvent, self).__init__(object)
        self.top_level_widget = tlw


class IndexChangedEvent(ObjectEvent):
    """Evento che segnala la variazione di indice di un modello"""

    implements(IIndexChangedEvent)

    def __init__(self, data_context, entity, index):

        super(IndexChangedEvent, self).__init__(data_context)
        self.entity = entity
        self.index = index


class ModelCursorChangedEvent(ObjectEvent):
    """Evento che segnala il cambiamento di stato di un cursore"""

    implements(IModelCursorChangedEvent)


class CommitChangesEvent(ObjectEvent):
    """Evento che segnala l'avvenuto commit"""

    implements(ICommitChangesEvent)