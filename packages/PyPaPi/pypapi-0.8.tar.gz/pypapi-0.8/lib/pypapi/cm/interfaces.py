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


import zope.interface
from zope import schema


class IContentManagement(zope.interface.Interface):

    uri = zope.interface.Attribute(u"Stringa di connessione al Content Management Server")


class IFolder(zope.interface.Interface):
    """
    Base class for a folder entity
    """

    files = schema.List(title=u"Files",
                        description=u"Files in the folder entity",)


class IFileItem(zope.interface.Interface):
    """
    A file in a folder entity
    """

    path = schema.TextLine(title=u"File path",
                           description=u"",)

    description = schema.TextLine(title=u"File description",
                                  description=u"",)