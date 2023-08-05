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


from sqlalchemy import Column, DefaultClause
from domains import timestamp_t, username_t

def addTimestamp(table):
    """Aggiungi i campi ereditati dalla tabella Timestamped.

    I campi vengono contrassegnati con un ``DefaultClause`` che indica
    a SQLAlchemy che il valore verrà assegnato dal database.
    """

    table.append_column(Column('rec_creato', timestamp_t, DefaultClause('when')))
    table.append_column(Column('rec_creato_da', username_t, DefaultClause('who')))
    table.append_column(Column('rec_modificato', timestamp_t, DefaultClause('when')))
    table.append_column(Column('rec_modificato_da', username_t, DefaultClause('who')))
