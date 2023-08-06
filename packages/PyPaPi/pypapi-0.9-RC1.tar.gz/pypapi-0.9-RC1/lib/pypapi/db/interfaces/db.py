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

class IDatabase(zope.interface.Interface):

    uri = zope.interface.Attribute(u"Stringa di connessione al database")

    echo = zope.interface.Attribute(u"Attiva la generazione dell'eco del "
                                    u"collquio con il server")

    ready = zope.interface.Attribute(u"Rivela lo stato del database")

    engine = zope.interface.Attribute(u"L'engine SQLAlchemy")

    session = zope.interface.Attribute(u"La sessione SQLAlchemy")

    def open(uri=None):
        """Apre la connessione al database.

        'uri' è la stringa opzionale per la connessione al database.
        questa variabile o l'attributo con lo stesso nome devono
        essere valorizzati perché l'operazione abbia successo."""

    def close(save=True):
        """Chiude la connessione al database e libera tutte le risorse utilizzate.

        'save' è opzionale e di default impostato a True. Indica se
        salvare i cambiamenti effettuati."""

class IDatabaseCreationEvent(zope.interface.Interface):
    """Evento utilizzato dal database per notificare la creazione di
    un nuovo oggetto IDatabase"""


class IDatabaseOpenedEvent(zope.interface.Interface):
    """Evento utilizzato dal database per notificare l'apertura"""


class IDatabaseClosedEvent(zope.interface.Interface):
    """Evento utilizzato dal database per notificare la chiusura"""


class IEntitiesRegistry(zope.interface.Interface):
    """Costruisce un mapping tra interfacce che implementano una certa
    interfaccia marker e delle classi che implementano tali interfacce."""


    def getEntityClassFor(interface):
        """Restituisce la classe che implementa una determinata
        interfaccia."""

    def getInterfaceFor(klass_or_inst):
        """Restituisce l'interfaccia implementata da una
        determinata entità."""


class IRelationResolver(zope.interface.Interface):
    """Data una interfaccia, da la possibilità di risolvere le
    relazioni tra gli oggetti espresse come dottednames e di ottenere
    l'interfaccia fornita dall'altro lato della relazione."""

    def resolveRelations(path):
        """Dato il percorso della relazione, restituisce due tuple
        contenenti rispettivamente i campi e le interfacce fornite da
        ogni 'hop' del percorso."""

    def resolveInterface(path):
        """Restituisce l'interfaccia target della risoluzione."""

    def resolveField(path):
        """Restituisce il campo che rappresenta l'ultima relazione."""

    def resolveSource(path):
        """Calcola la sorgente per il dato path di relazione."""


class ITraverser(zope.interface.Interface):
    """Data una interfaccia ed un campo che esprime una relazione con
    un altro tipo di oggetto, un traverser può essere in grado di
    calcolare l'interfaccia fornita da un eventuale oggetto che può
    valorizzare il campo."""

    def traverse():
        """Esegue il calcolo"""