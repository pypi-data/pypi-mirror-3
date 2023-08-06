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


from zope.interface.interfaces import IInterface
from zope.schema import Object
from zope.schema.interfaces import WrongType


class DbObject(Object):
    """Versione particolare di zope.schema.Object che se non fornito,
    calcola lo schema dal layer SQLAlchemy."""

    def __init__(self, schema=None , **kw):

        super(Object, self).__init__(**kw)
        self._schema = schema
        if schema is not None:
            if not IInterface.providedBy(schema):
                raise WrongType

    def _setSchema(self, value):

        self._schema = value

    def _getSchema(self):

        if self._schema is None:
            from  pypapi.db.satraverser import SARelationTraverser
            traverser = SARelationTraverser(self.interface, self)
            return traverser.traverse()
        return self._schema

    schema = property(_getSchema, _setSchema)
