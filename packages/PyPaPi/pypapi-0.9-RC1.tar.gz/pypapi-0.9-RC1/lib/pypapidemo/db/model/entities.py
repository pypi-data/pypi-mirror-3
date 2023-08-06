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

import os
import zope.interface
from pypapi.db.model.entities.base import EntitaBase
from pypapidemo.db.interfaces import *


class Genre(EntitaBase):

    zope.interface.implements(IGenre)

    def getCaption(self):
        return self.description


class Author(EntitaBase):

    zope.interface.implements(IAuthor)

    def getCaption(self):
        return "%s %s" % (self.name, self.surname)


class Book(EntitaBase):

    zope.interface.implements(IBook)

    def getCaption(self):
        return "%s (%s)" % (self.title, self.author.caption)



__all__ = ['Book', 'Author', 'Genre']