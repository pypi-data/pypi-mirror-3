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
import zope.schema
from pypapi.db.source import GenericSource
from pypapi.db.interfaces import IEntitaBase

class ICriterion(zope.interface.Interface):

    term = zope.schema.Choice(title=u"Termine di ricerca",
                              required=True,
                              source=GenericSource('context.search.getPossibleTerms'))

    value = zope.schema.TextLine(title=u"Valore",
                                 required=False)

    search = zope.interface.Attribute(u"La ricerca alla quale questo criterio è associato")

    def getCriterionItems():
        """Restituisce una tupla contenente elementi (term, parametro
        ricerca) che servono per creare query di ricerca sulla sorgente."""

class ISearch(zope.interface.Interface):

    description = zope.schema.TextLine(title=u"Descrizione")

    criteria = zope.schema.List(title=u"Criteri",
                                description=u"Criteri che compongono questa ricerca",
                                readonly=True,
                                value_type=zope.schema.Object(title=u"Criterio",
                                                              schema=ICriterion))

    source = zope.interface.Attribute(u"Sorgente utilizzata da questa ricerca")

    def querySource():
        """Interroga la sorgente e restituisce una nuova sorgente che
        genera elementi che rispondono ai criteri di questa ricerca."""

    def getPossibleTerms():
        """Restituisce la lista di termini per i quali è possibile
        associare un criterio di ricerca."""

    def addCriterion(term_key, query_value):
        """Aggiunge un criterio al set di quelli associati a questa
        ricerca."""

class ITerm(IEntitaBase):

    key = zope.schema.TextLine(title=u"La chiave del termine",
                               description=u"La chiave del termine (corrispondente al nome di un " + \
                               u"campo di una determinata interfaccia)")

class ISearchableTerms(zope.interface.Interface):
    """Interfaccia che serve da colla tra una qualsiasi Interface ed
    il sistema di ricerca al fine scoprire quali campi di tale
    interfaccia sono ricercabili. Uno specifico adattatore per un
    certo tipo di interfaccia (IORM) nel caso più ovvio, si incarica
    di implementarla"""

    def getTerms():
        """Restituisce la lista di termini per i quali è possibile
        associare un criterio di ricerca."""
