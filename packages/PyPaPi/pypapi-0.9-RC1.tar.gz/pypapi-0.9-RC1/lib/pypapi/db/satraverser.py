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
from zope.component import getGlobalSiteManager
from zope.schema.interfaces import IChoice, ICollection
from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import InvalidRequestError
from pypapi.db.interfaces import ITraverser, IEntitiesRegistry, IEntitaBase

gsm = getGlobalSiteManager()


class SARelationTraverser(object):
    """Data un'interfaccia che implementa IORM e un campo, restituisce
    l'interfaccia IORM che caratterizza gli elementi che valorizzano
    il campo. Per dirla più brevemente, fa affiorare in maniera più
    generica il concetto di relazione SA."""

    implements(ITraverser)

    def __init__(self, left_interface, field):

        self.left_interface = left_interface
        self.field = field

    def traverse(self):

        reg = gsm.getUtility(IEntitiesRegistry)
        _class = reg.getEntityClassFor(self.left_interface)
        rel_name = self.field.__name__
        mapper = class_mapper(_class)
        try:
            submap = mapper.get_property(rel_name).mapper
            entity_class = submap.class_
            right_interface = reg.getInterfaceFor(entity_class)
            return right_interface
        except InvalidRequestError:
            try:
                interface = self.left_interface.get(rel_name).getTaggedValue('interface')
            except KeyError:
                interface = IEntitaBase
            finally:
                return interface

gsm.registerSubscriptionAdapter(SARelationTraverser, required=(IInterface, IChoice))
gsm.registerSubscriptionAdapter(SARelationTraverser, required=(IInterface, ICollection))
