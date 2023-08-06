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


from zope.interface import Attribute, Interface
from zope.schema.interfaces import IIterableSource


class IDbSource(IIterableSource):
    """Una sorgente che contiene valori proveninenti dal DB S.A."""

    query = Attribute("La query S.A. che viene usata come sorgente")

    specs = Attribute("Le ulteriori specifiche di filtro che sono state specificate"
                      " al momento della creazione")

    item_interface = Attribute("L'interfaccia esportata dagli elementi che vengono"
                               " generati da questa sorgente")

    limit = Attribute("Limit: numero massimo di entità estratte"
                      "in caso di ricerche filtrate.")


    def refresh():
        """Riesegue la query"""

    def filter(self, *specs):
        """Restituisce una nuova sorgente filtrata secondo le specifiche."""


class IDbSourceFactory(Interface):
    """Una factory in grado di creare una sorgente IDbSource sulla sessione data"""