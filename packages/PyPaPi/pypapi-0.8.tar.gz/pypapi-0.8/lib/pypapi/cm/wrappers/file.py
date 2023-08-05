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
from shutil import copyfile
from base import BasicWrapper
from pypapi.cm.fileitem import FileItem


class CMWrapper(BasicWrapper):

    def __init__(self, uri=None, username=None, password=None):
        super(CMWrapper, self).__init__(uri)

    def getFiles(self, folder_path):
        """
        Lettura dei file da file system
        nota: per ora viene ignorata la parte di percorso
        nell'uri
        """
        files = []
        for file_name in os.listdir(folder_path):
            ext = file_name.split('.')[-1]
            file_path = os.path.join(folder_path, file_name)
            files.append(FileItem(file_path, '%s document' % ext.upper()))
        return files

    def appendFile(self, file_path, folder_path):
        """
        Copia il file nella destinazione
        """
        copyfile(file_path, folder_path)
