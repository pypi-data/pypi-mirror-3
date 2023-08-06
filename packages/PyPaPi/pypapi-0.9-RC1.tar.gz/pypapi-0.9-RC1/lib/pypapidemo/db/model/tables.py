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

from sqlalchemy import Column, Table, ForeignKeyConstraint, Sequence
from sqlalchemy import UnicodeText, Integer
from pypapi.db.model.meta import metadata


genres = Table('genres', metadata,
    Column('idgenre', Integer, Sequence('idgenre_seq'), primary_key=True),
    Column('description', UnicodeText),
    )


authors = Table('authors', metadata,
    Column('idauthor', Integer, Sequence('idauthor_seq'), primary_key=True),
    Column('name', UnicodeText),
    Column('surname', UnicodeText),
    )


books = Table('books', metadata,
    Column('idbook', Integer, primary_key=True),
    Column('isbn', UnicodeText),
    Column('title', UnicodeText),
    Column('idauthor', Integer),
    Column('idgenre', Integer),
    Column('description', UnicodeText),
    ForeignKeyConstraint(['idauthor'], ['authors.idauthor']),
    ForeignKeyConstraint(['idgenre'], ['genres.idgenre']),
    )
