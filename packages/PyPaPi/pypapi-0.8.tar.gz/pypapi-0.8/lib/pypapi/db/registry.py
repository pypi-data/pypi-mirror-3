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


from ZConfig import ConfigurationError

from zope.interface import implementedBy, implements
from zope.component import adapter, provideHandler, getUtilitiesFor, provideUtility, getUtility
from zope.component.interfaces import ComponentLookupError
from pypapi.db.interfaces import IDatabaseCreationEvent, IORM, IEntitiesRegistry

class EntitiesRegistry(object):
    """Costruisce un mapping tra interfacce che implementano una certa
    interfaccia marker e delle classi che implementano tali interfacce."""

    implements(IEntitiesRegistry)

    def __init__(self, interfaces, entities):
        i2e = {}
        e2i = {}
        for entity in entities:
            # assumo una corrispondenza biunivoca
            for i in implementedBy(entity):
                if i in interfaces:
                    i2e[i] = entity
                    e2i[entity] = i
                    break # XXX prendo la prima anziché l'ultima...
        self.e2i, self.i2e = e2i, i2e

    def getEntityClassFor(self, interface):
        """Restituisce la classe che implementa una determinata
        interfaccia, posto che tale interfaccia implementi IORM."""
        try:
            return self.i2e[interface]
        except KeyError:
            raise ConfigurationError("L'interfaccia %s non risulta associata ad alcuna entity"
                                     % interface)

    def getInterfaceFor(self, klass_or_inst):
        """Restituisce l'interfaccia marcata come IORM implementata da una
        determinata entità."""
        try:
            if isinstance(klass_or_inst, type):
                return self.e2i[klass_or_inst]
            else:
                return self.e2i[klass_or_inst.__class__]
        except KeyError:
            raise ConfigurationError("L'entity %s non risulta associata ad alcuna interfaccia IORM"
                                     % repr(klass_or_inst))

@adapter(IDatabaseCreationEvent)
def initRegistry(event):
    orm_interfaces = [item[1] for item in getUtilitiesFor(IORM)]

    from pypapi.db.interfaces import ILibraryName
    try:
        #library_name = getUtility(ILibraryName)
        libraries = getUtility(ILibraryName)
        if isinstance(libraries, str):
            libraries = [libraries,]
        orm_entities = []
        for library_name in libraries:
            _temp = __import__('%s.db.model'%library_name, globals(), locals(), ['entities'])
            extraentities = _temp.entities
            orm_entities.extend([getattr(extraentities, cn) for cn in extraentities.__all__])
    except ComponentLookupError:
        pass

    sa_registry = EntitiesRegistry(orm_interfaces, orm_entities)
    provideUtility(sa_registry, provides=IEntitiesRegistry)

provideHandler(initRegistry)
