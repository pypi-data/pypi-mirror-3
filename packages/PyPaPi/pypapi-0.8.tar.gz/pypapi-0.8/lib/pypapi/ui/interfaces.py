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

class IListModel(zope.interface.Interface):

    def rowCount(parent=None):
        """Numero di righe del modello."""

    def data(index, role=None):
        """Restituisce il dato contenuto sotto il ruolo 'role' all'indice passato."""

    def setData(index, value, role):
        """Setta nel modello il valore all'indice dato. A buon fine restituisce True."""

    def flags(index):
        """Restituisce i flag di accesso all'item in index."""


class ITableModel(zope.interface.Interface):

    def rowCount(parent=None):
        """Numero di righe del modello."""

    def columnCount(parent=None):
        """Numero di colonne del modello."""

    def data(index, role=None):
        """Restituisce il dato contenuto sotto il ruolo 'role' all'indice passato."""

    def setData(index, value, role):
        """Setta nel modello il valore all'indice dato. A buon fine restituisce True."""

    def flags(index):
        """Restituisce i flag di accesso all'item in index."""
