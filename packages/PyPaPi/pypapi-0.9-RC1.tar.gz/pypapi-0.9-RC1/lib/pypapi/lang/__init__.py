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

from PyQt4 import QtCore
from pkg_resources import resource_filename

def installTranslator(app, library_name='pypapi'):
    """
    Install the locale PyPaPi translator
    """
    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()
    qm_file = resource_filename('%s.lang' % library_name, '%s_%s' % (library_name, locale))
    if translator.load(qm_file):
        app.installTranslator(translator)
