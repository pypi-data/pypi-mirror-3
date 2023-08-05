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
from logging import getLogger
from base import BasicWrapper
from pypapi.cm.fileitem import FileItem
try:
    from cmislib.model import CmisClient, ACE
    from cmislib.exceptions import ObjectNotFoundException
    CMIS_ON = True
except:
    CMIS_ON = False

logger = getLogger('cmis')


class CMWrapper(BasicWrapper):


    def __init__(self, uri=None, username=None, password=None):
        if CMIS_ON is False:
            logger.error('Unable to import cmslib')
        super(CMWrapper, self).__init__(uri)
        self.http_uri = self.uri.replace('cmis:', 'http:')
        self.host, other = self.http_uri[7:].split(':')
        self.port = other.split('/')[0]
        logger.debug('Connect to %s' % self.uri)
        self.client = CmisClient(self.http_uri, username, password)


    def getFiles(self, folder_path):
        """
        Lettura dei file da server compatibile cmis. Restituisce una lista di FileItem.
        Se il percorso non è presente, lo crea.
        """
        files = []
        repo = self.client.getDefaultRepository()
        logger.debug('Access to %s folder (getFiles)' % folder_path)
        tkns = folder_path.split('/')
        n = len(tkns)
        folder = None
        for i in range(n, 0, -1):
            path = '/'.join(tkns[:i])
            try:
                folder = repo.getObjectByPath('/%s' % path)
                break
            except ObjectNotFoundException:
                logger.debug('Object %s not found' % path)
                continue
        if folder is None:
            folder = repo.getObjectByPath('/')
            i -= 1
        if i < n:
            for j in range(i, n):
                folder = folder.createFolder(tkns[j])
                logger.debug('Folder %s created' % tkns[j])
        self.folder = folder
        for child in self.folder.getChildren():
            ext = child.name.split('.')[-1]
            _id = str(child.id)
            files.append(FileItem(_id, child.name, '%s document (%s)' % (ext.upper(), _id)))
        return files


    def appendFile(self, file_path, folder_path):
        """
        Inserisce il nuovo file
        """
        file_name = file_path.split(os.path.sep)[-1]
        f = open(file_path, 'rb')
        doc = self.folder.createDocument(file_name, contentFile=f)
        f.close()
