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
import sys
import base64
from subprocess import Popen, PIPE
from logging import getLogger
from zope.interface import implements
from zope.component import provideUtility, getUtility
from pypapi.cm.interfaces import IContentManagement
from pypapi.db.interfaces import IAuthentication

logger = getLogger('cm')

class ContentManagement(object):
    """Gestisce la connessione al Content Management Server"""

    implements(IContentManagement)


    def __init__(self, uri=None):
        """"""
        self.uri = uri
        self.wrapper_type = None
        if uri is not None:
            self.open(uri, folder)


    def open(self, uri):
        """
        Crea il wrapper del tipo indicato in uri
        """
        self.wrapper_type = uri.split(':')[0]
        if '@' in uri:
            pre_at, post_at = uri.split('@')
            username, password = pre_at.split('//')[-1].split(':')
            self.uri = '%s://%s' % (self.wrapper_type, post_at)
        else:
            # se username e password non sono dichiarati, provo ad usare le credenziali
            # di accesso al database
            auth = getUtility(IAuthentication)
            username, password = base64.decodestring(auth).split(':')
            username = username or None
            password = password or None
            self.uri = uri
        _temp = __import__('wrappers.%s' % self.wrapper_type, globals(), locals(), ['CMWrapper'])
        self.wrapper = _temp.CMWrapper(self.uri, username, password)
        logger.debug('Configure %s content management wrapper' % self.wrapper_type)

    # proxy dei metodi sul wrapper
    getFiles = lambda self, folder: self.wrapper.getFiles(folder)
    openFile = lambda self, _id: self.wrapper.openFile(_id)
    appendFile = lambda self, folder, file: self.wrapper.appendFile(folder, file)


    def openFileFromId(self, _id):
        pars = {'id':_id}
        if '%(username)s' in self.wrapper.base_file:
            auth = getUtility(IAuthentication)
            pars['username'], pars['password'] = base64.decodestring(auth).split(':')
        file_path = self.wrapper.base_file % pars
        self.openFile(file_path)


    def openFile(self, file_path):
        """
        Determina sulla base del sistema operativo il comando da utilizzare per aprire
        un file con l'editor predefinito di sistema, e lo apre restituendo il suo
        subprocess.
        """
        name = None
        try:
            # osx -> 'Darwin', linux -> 'Linux'
            name = os.uname()[0]
        except AttributeError:
            import sys
            i = sys.getwindowsversion()[3]
            if i == 1:
                name = 'Win95-98-me'
            elif i == 2:
                name = 'WinNT-2k-xp-x64'
        if name == 'Win95-98-me':
            com = '"%s"'
        elif name == 'WinNT-2k-xp-x64':
            com = '"%s"'
        elif name == 'Darwin':
            com = 'open --wait-apps "%s"'
        elif name == 'Linux':
            com = 'desktop-launch "%s"' # 'kde-open' per kde (variabile desktop)
        p = Popen([com % file_path], shell=True, stdin=PIPE, stdout=PIPE, close_fds=False)
        return p


    def openFolder(self, folder_path):
        """
        Apre la folder utilizzando il config.base_folder nel cm
        """
        pars = {'folder_path':folder_path}
        if '%(username)s' in self.wrapper.base_folder:
            auth = getUtility(IAuthentication)
            pars['username'], pars['password'] = base64.decodestring(auth).split(':')
        folder = self.wrapper.base_folder % pars
        self.openFile(folder)


def createContentManagement(uri=None):
    cm_utility = ContentManagement(uri=uri)
    provideUtility(cm_utility, provides=IContentManagement)
    return cm_utility