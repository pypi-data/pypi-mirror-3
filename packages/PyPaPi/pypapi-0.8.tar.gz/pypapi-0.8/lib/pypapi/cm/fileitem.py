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

import logging
from zope.interface import implementedBy, implements
from pypapi.cm.interfaces import IFileItem


logger = logging.getLogger('model')


class FileItem(object):
    """
    Oggetto che rappresenta la singola risorsa (in genere un file o una cartella) all'interno
    del CMS.

    ident: l'id utilizzato nel CMS
    name: il nome del file
    description: la descrizione
    """

    implements(IFileItem)

    def __init__(self, _id, name, description=''):
        self.id = _id
        self.name = name
        self.description = description