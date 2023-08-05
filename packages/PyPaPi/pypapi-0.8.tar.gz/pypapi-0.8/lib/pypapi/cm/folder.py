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
from datetime import date, datetime
from sqlalchemy.orm.util import class_mapper
from zope.interface import implements
from zope.component import getUtility
from pypapi.cm.interfaces import IFolder
from pypapi.cm.fileitem import FileItem
from pypapi.cm.interfaces import IContentManagement

EXCLUDES = ('CAPTION_TRIM_CHAR', 'CAPTION_TRIM_LENGTH', 'files', 'folder_path')


class Container(list):
    """
    Classe contenitore, che si comporta come una lista, esponendo le caratteristiche
    del Content Management
    """

    def __init__(self, folder_path):
        self.folder_path = folder_path
        cm = getUtility(IContentManagement)
        self._folder = cm.getFiles(self.folder_path)
        self.idx = -1

    # API list

    def __iter__(self):
        return self

    def next(self):
        """Iterazione"""
        self.idx += 1
        if self.idx >= len(self._folder):
            raise StopIteration
        return self._folder[self.idx]

    def __repr__(self):
        return self._folder.__repr__()

    def __getitem__(self, index):
        return self._folder[index]

#     def __setitem__(self, index, item):
#         self._folder.__setitem__(index, item)
#
#     def __delitem__(self, index):
#         self._folder.__delitem__(index)

    def append(self, item):
        file_path = str(item.path())
        src = file_path
        dst = os.path.sep.join((self.folder_path, file_path.split(os.path.sep)[-1]))
        cm = getUtility(IContentManagement)
        cm.appendFile(src, dst)
        self._folder = cm.getFiles(self.folder_path)

#    def pop(self, index=-1):
#        return self._folder.pop(index)

#    def remove(self, index):
#        self._folder.remove(index)

    def insert(self, index, item):
        """La folder non è ordinata"""
        self.append(item)
        self._folder.insert(index, item)


class Folder(object):

    implements(IFolder)

    def getFiles(self):
        container = Container(self.folder_path)
        return container
    files = property(getFiles)

    def getFolderPath(self):
        """Costruisce il percorso della cartella a cui punta il CM"""
        cm = getUtility(IContentManagement)
        d = {}
        for attr_name in dir(self):
            if attr_name in EXCLUDES or attr_name[:2] == '__':
                continue
            attr = getattr(self, attr_name)
            if isinstance(attr, (str, int, float, unicode)):
                d[attr_name] = attr
            elif isinstance(attr, (date, datetime)):
                d['%s_year' % attr_name] = attr.year
                d['%s_month' % attr_name] = attr.month
                d['%s_day' % attr_name] = attr.day
        d['type'] = self.__class__.__name__
        if "%(id)s" in cm.wrapper.folder_path:
            # ottimizzazione: se non uso id, non interrogo il mapper
            table = class_mapper(self.__class__).mapped_table
            d['id'] = '_'.join([str(getattr(self, pk.key)) for pk in table.primary_key])
        return cm.wrapper.folder_path % d
    folder_path = property(getFolderPath)
