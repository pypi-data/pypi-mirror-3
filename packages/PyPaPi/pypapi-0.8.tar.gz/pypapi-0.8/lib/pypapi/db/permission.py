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
from zope.component import adapter, provideHandler, provideUtility, getUtility
from pypapi.db.interfaces import IDatabaseCreationEvent

from sqlalchemy.orm.util import class_mapper
from pypapi.db.interfaces import IEntitiesRegistry, IDatabase, IPermission


class Permission(object):
    """
    Utility per far emergere le policy del database.
    """

    implements(IPermission)

    def resolvePermissions(self, interface):
        registry = getUtility(IEntitiesRegistry)
        db = getUtility(IDatabase)
        if db.engine.dialect.name not in ('postgres', 'postgresql'):
            return True, True, True, True
        klass = registry.getEntityClassFor(interface)
        mapper = class_mapper(klass)
        table = mapper.mapped_table
        table_name = str(table).split(' ')[0]
        sqlstr = "SELECT has_table_privilege('%s', '%s');"
        privileges = []
        for to_check in ('select', 'insert', 'update', 'delete'):
            res = db.engine.execute(sqlstr % (table_name, to_check))
            for row in res:
                privileges.append(row[0])
        return privileges


@adapter(IDatabaseCreationEvent)
def initPermission(event):
    p = Permission()
    provideUtility(p, provides=IPermission)

provideHandler(initPermission)