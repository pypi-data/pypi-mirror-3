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

from zope import schema
from zope.component.interface import provideInterface
from zope.component import provideUtility
from pypapi.db.field import DbObject
from pypapi.db.interfaces import IORM
from pypapi.db.interfaces.base import IEntitaBase


class IAuthor(IEntitaBase):
    """
    Author
    """

    idauthor = schema.Int(title = u"ID author",
                 description = u"Unique ID")

    name = schema.TextLine(title = u"Name",
             description = u"Name")

    surname = schema.TextLine(title = u"Surname",
               description = u"Surname")

    books =  schema.List(title=u"Books",
              description=u"Author's books",
              readonly=True,
              value_type=DbObject(title=u"Book"))

class IGenre(IEntitaBase):
    """
    Book genre
    """

    idgenre = schema.Int(title = u"ID genre",
                description = u"Unique ID")

    description = schema.TextLine(title = u"Description",
                    description = u"Short description")


def checkISBN(value):
    """Dummy ISBN check (es. 978-88-11-68102-1)"""
    chars = [str(s) for s in list(value)]
    pattern = list("000-00-00-00000-0"[:len(chars)])
    numbers = [str(n) for n in range(10)]
    for i in range(len(chars)):
        c = str(chars[i])
        o = ord(c)
        if pattern[i] == "0" and not (o > 47 and o < 58):
            return False
        elif pattern[i] == "-" and c != "-":
            return False
    return True


class IBook(IEntitaBase):
    """
    Book interface
    """

    isbn = schema.TextLine(title = u"ISBN",
             description = u"Isbn book code",
             max_length = 17,
             constraint = checkISBN,
             )

    title = schema.TextLine(title = u"Title",
               description = u"Book title",
               max_length = 25)

    author = DbObject(title = u"Author",
               description = u"Book's author")

    genre = DbObject(title = u"Genre",
              description = u"Book's genre")

    description = schema.Text(title = u"Description",
                    description = u"Short description")


for i in (IGenre, IAuthor, IBook,):
    provideInterface('', i, IORM)
    provideUtility(i, IORM, name=i.__name__)
