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


from zope.interface import implements
from zope.component import provideAdapter, adapts
from zope.schema import getFieldsInOrder, Int, Text
from pypapi.db.interfaces import IORM
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.search.interfaces import ICriterion, ISearch, ISearchableTerms, \
     ITerm

class SimpleCriterion(object):

    implements(ICriterion)

    def __init__(self, search, term=None, value=''):

        self.search = search
        self.term = term
        self.value = value

    def getCriterionItems(self):

        if (self.term is not None) and (len(self.value.strip()) > 0):
            yield self.term.key, self.value
        else:
            return


class Search(object):

    implements(ISearch)
    adapts(IDbSource)

    def __init__(self, source, description=''):

        self.source = source
        self.criteria = []
        self.description = description

    def getPossibleTerms(self):
        """Utilizzato nel campo 'term' definito sull'interfaccia ICriterion"""
        terms = ISearchableTerms(self.source.item_interface).getTerms()
        return terms

    def addCriterion(self, term_key, query_value=''):

        # verifico la chiave
        # perché ricalcolare il mapping ogni volta?
        terms_map = dict([(t.key, t) for t in self.getPossibleTerms()])
        if terms_map.has_key(term_key):
            criterion = SimpleCriterion(self, terms_map[term_key], query_value)
            self.criteria.append(criterion)
        else:
            raise ValueError("Termine non valido per questa ricerca: '%s'" % term_key)

    def querySource(self):

        # raccolgo i termini di ricerca
        from itertools import chain
        crit_iters = [c.getCriterionItems() for c in self.criteria]
        crit_items_iter = chain(*crit_iters)
        return self.source.filter(crit_items_iter)

provideAdapter(Search)

class Term(object):

    implements(ITerm)

    def __init__(self, key):

        self.key = key

    def getCaption(self):

        return self.key


class ORMSearchableTerms(object):

    implements(ISearchableTerms)
    adapts(IORM)

    def __init__(self, orm_interface):

        self.orm_interface = orm_interface

    def getTerms(self):

        fields = getFieldsInOrder(self.orm_interface)
        # prendo solo i campi interi e di testo
        filtered = []
        for name, f in fields:
            if isinstance(f, Int) or isinstance(f, Text):
                filtered.append(f)
        terms = [Term(f.__name__) for f in filtered]
        return terms

provideAdapter(ORMSearchableTerms)
