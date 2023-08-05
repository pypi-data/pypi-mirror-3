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

from PyQt4 import QtGui, QtCore
from logging import getLogger
import zope.interface
from zope import schema
from interfaces import IValidator

logger = getLogger('cute')

class Validator(QtGui.QValidator):
    """Classe base dei validatori per i widget"""

    zope.interface.implements(IValidator)

    def __init__(self, parent=None, max_length=0, constraint=None):
        self.max_length = max_length
        self.constraint = constraint
        QtGui.QValidator.__init__(self, parent)

    def validate(self, value, pos):
        ok = True
        if self.max_length > 0 and len(value) > self.max_length:
            return QtGui.QValidator.Invalid, pos
        if self.constraint(value) in (None, False):
            return QtGui.QValidator.Invalid, pos
        return QtGui.QValidator.Acceptable, pos

    def fixup(self, value=None):
        return


def addValidatorsFor(form):
    """Esegue il bind dei validatori ai widget della form"""
    names = form.interface.names(all=True)
    for name in dir(form):
        w = getattr(form, name)
        if isinstance(w, (QtGui.QLineEdit,)):
            # preferisco la proprietà column all'object-name
            try:
                k = w.column
            except AttributeError:
                k = name
            f = form.interface.get(k)
            if f is None:
                msg = 'Validator binding fail: unable to get %s from %s' % (k, form.interface.__name__)
                logger.debug(msg)
                continue
            if isinstance(f, schema.TextLine):
                max_length = f.max_length
            else:
                max_length = None
            v = Validator(max_length=max_length, constraint=f.constraint)
            w.setValidator(v)
