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


from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.component import getGlobalSiteManager, adapts, queryAdapter
from zope.schema.interfaces import IObject, ICollection, IField, IIterableSource
from pypapi.db.interfaces import IRelationResolver, ITraverser

gsm = getGlobalSiteManager()


class PathRelationResolver(object):

    implements(IRelationResolver)
    adapts(IInterface)
    context = None

    def __init__(self, root_interface):

        self.root_interface = root_interface

    def resolveRelations(self, path):

        root_interface = self.root_interface
        fragments = path.split('.')
        interfaces = []
        fields = []
        interfaces.append(root_interface)
        if path == '.':
            return fields, interfaces
        for ix, fragment in enumerate(fragments):
            if ix == 0: continue
            interface = interfaces[ix - 1]
            field = interface.get(fragment)
            if (field is None) or not IField.providedBy(field):
                raise ValueError("Il frammento '%s' del path '%s' non è il nome di un campo" %  \
                                 (fragment, path))
            traversers = gsm.subscribers((interface, field), ITraverser)
            interface = None
            for t in traversers:
                interface = t.traverse()
                if interface is not None:
                    break
            fields.append(field)
            interfaces.append(interface)
        return fields, interfaces


    def resolveInterface(self, path):

        fields, interfaces = self.resolveRelations(path)
        return interfaces.pop()


    def resolveField(self, path):

        fields, interfaces = self.resolveRelations(path)
        if len(fields) > 0:
            return fields.pop()
        else:
            return None

    def resolveSource(self, path):

        fields, interfaces = self.resolveRelations(path)
        # la sorgente è calcolata considerando per ora due sole
        # modalità, una specifica dell'oggetto che contiene quello
        # potenziale da assegnare e l'altra generica dell'interfaccia
        # richiesta, con una preferenza per la sorgente più
        # specifica e in caso non esista un fallback sulla sorgente
        # generica per quella interfaccia
        if (self.context is not None) and (len(interfaces) >= 2):
            assert len(fields) >= 1
            right = interfaces.pop()
            # primo tentativo
            source = queryAdapter(self.context.parent_entity, IIterableSource,
                                  self.context.field.__name__)
            if source is None:
                # fallback
                source = IIterableSource(right)
            return source
        # fallback generico
        interface = interfaces.pop()
        return IIterableSource(interface)

    def bind(self, data_context):

        self.context = data_context

gsm.registerAdapter(PathRelationResolver)


class GenericObjectTraverser(object):
    """Risolve la relazione (o cerca di farlo) nel caso in cui il
    campo supporti IObject come zope.schema.object."""

    implements(ITraverser)
    adapts(IInterface, IField)

    def __init__(self, left_interface, field):

        self.left_interface = left_interface
        self.field = field

    def traverse(self):

        field = self.field
        if ICollection.providedBy(field):
            field = field.value_type
            # patch interface quando un IObject si trova all'interno
            # di una lista
            field.interface = self.field.interface
            field.__name__ = self.field.__name__
        if IObject.providedBy(field):
            return field.schema

gsm.registerSubscriptionAdapter(GenericObjectTraverser)
