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
import zope.component.interfaces


class IObject(zope.interface.Interface):
    """Ogni oggetto QT implementa questa interfaccia"""

    def objectName():
        "il nome del widget specificato nel designer"

    def parent():
        "Il widget che contiene questo widget, se esistente."

    def setParent(parent):
        "Imposta il parent"

    def children():
        "Restituisce i figli"

    def connect(sender, signal, callable):
        """Connette il widget al segnale emesso da un altro
        widget. Questa è solo una delle possibili signatures del
        metodo"""

    def disconnect(signal):
        """Disconnette un segnale. Questa è solo una delle possibili
        signatures del metodo"""

    def emit(signal, *args):
        "Emette il segnale specificato"


class IModel(IObject):
    """Espone uno store alla GUI Qt come una serie di items
    individuati per riga e colonna."""

    store = zope.interface.Attribute('Lo store contiene o è preposto a contenere'
                                     ' le istanze di oggetti di cui è responsabile'
                                     ' questo modello.')


class ITreeModel(IObject):
    """Espone uno store alla GUI Qt come una serie di items
    individuati per riga, colonna, e parent"""

    store = zope.interface.Attribute('Lo store contiene o è preposto a contenere'
                                     ' le istanze di oggetti di cui è responsabile'
                                     ' questo modello.')


class IMapper(IObject):
    """Consente di legare dei comuni widget per le forms ad un modello"""

    def model():
        "Il modello utilizzato"

    def setModel():
        "Imposta il modello"

    def addMapping(widget, col_index):
        "aggiunge un mapping tra il model e il widget"


class IColumn(zope.interface.Interface):
    """Rappresenta la singola colonna che compone il modello."""
    # XXX da completare


class IIndexedColumn(IColumn):
    """Una colonna che contiene un indice delle istanze dello store"""


class IDataItem(zope.interface.Interface):
    """Espone il singolo valore esposto dal modello. Gli oggetti GUI
    Qt necessitano di maggiori informazioni rispetto alla semplice
    valorizzazione offerta dallo store. Queste sono determinate
    attraverso 12 ruoli e 8 flags che la vista chiede al modello di
    valorizzare. Gli oggetti che forniscono questa interfaccia,
    coadiuvati dalla colonna ed eventualmente dal campo
    (zope.schema.IField), forniscono tali informazioni."""
    # XXX da completare


class IValidator(IObject):
    """Consente di eseguire la validazione di un valore inserito in un widget,
    prima che il modello cerchi di assengarlo alla proprietà dell'oggetto"""

    def validate(value):
        "Esegue le validazioni"

    def fixup(value):
        ""


class IForm(IObject, zope.component.interfaces.IComponents):
    """Interfaccia esportata dalla singola Form"""

    parent = zope.interface.Attribute("L'oggetto application o la form che la contiene")

    ui_filename = zope.interface.Attribute("Il nome del file contenente la descrizione xml della form")


class IDataForm(IForm):

    interface = zope.interface.Attribute("L'interfaccia che tutti gli items implementano")


class IStoreEditForm(IDataForm):
    """Form che visualizza il contenuto di uno store"""

    store = zope.interface.Attribute('Lo store contiene o è preposto a contenere'
                                     ' le istanze di oggetti che verranno manipolati da questa form')

    factory = zope.interface.Attribute('La factory utilizzata per generare nuove istanze di items')


class IPyPaPiForm(zope.interface.Interface):
    """Interfaccia della form specifica per le applicazioni PyPaPi"""

class IPyPaPiDialog(zope.interface.Interface):
    """Interfaccia della dialog specifica per le applicazioni PyPaPi"""

class IMainWindow(zope.interface.Interface):
    """Interfaccia della form principale dell'applicazione"""


class IDataContext(zope.interface.Interface):
    """Il contesto dati associato ad ogni Widget"""


class IWidgetCreationEvent(zope.component.interfaces.IObjectEvent):
    """Evento scatenato dal loader nel momento in cui viene creato un nuovo oggetto"""

    top_level_widget = zope.interface.Attribute("Il widget esterno, che contiene tutti gli altri,"
                                                " in genere, la form")


class IIndexChangedEvent(zope.component.interfaces.IObjectEvent):
    """Evento scatenato dal cambio di indice di un modello"""

    entity = zope.interface.Attribute("La relazione che ha generato l'evento")
    index = zope.interface.Attribute("La nuova posizione")


class IWidget(IObject):
    """L'interfaccia minima di accesso al widget"""


class ISimpleDataWidget(IWidget):
    """Interfaccia marker implementata da quei widgets che consentono
    di visualizzare una singola colonna del modello."""


class IPickerEntityWidget(IWidget):
    """Interfaccia marker per il widget pickerentity al fine di
    personalizzare il binding ai dati. XXX da rimuovere quando verrà
    utilizzata la lib PyQt4.4 dove possibile specificare il flag
    'user' su pyqtProperty."""


class INullableDateEditWidget(IWidget):
    """Interfaccia marker per il widget NullableDateEdit."""


class INullableDateTimeEditWidget(INullableDateEditWidget):
    """Interfaccia marker per il widget NullableDateTimeEdit."""


class ISelectForm(IForm):
    """Interfaccia per il widget in grado di fornire una ricerca e selezione."""

    parent_form = zope.interface.Attribute("La form da cui viene richiamata la SelectForm")

class ISelectFormLite(ISelectForm):
    """Come la ISelectForm, ma con layout più leggero."""


class IQuickInsertForm(IForm):
    """Interfaccia per il widget in grado di eseguire un inserimento veloce."""


class ILookupDataWidget(IWidget):
    """Interfaccia marker implementata da quei widgets che utilizzano
    un modello di lookup per consentire la scelta tra un set di
    valori."""

    def currentIndex():
        """Contiene l'indice del valore selezionato nel modello di
        lookup"""

    def setCurrentIndex(index):
        "imposta l'indice del valore selezionato"

    def model():
        "Il modello di lookup utilizzato"

    def setModel():
        "Imposta il modello di lookup"


class IModelView(IWidget):
    """Interfaccia marker implementata da quei widgets che
    visualizzano un intero modello"""

    def model():
        "Il modello utilizzato"

    def setModel():
        "Imposta il modello"


class ITreeModelView(IWidget):
    """Interfaccia marker implementata da quei widgets che
    visualizzano un intero modello come tree"""

    def model():
        "Il modello utilizzato"

    def setModel():
        "Imposta il modello"


class IModelCursor(IWidget):
    """Rappresenta il cursore in una sequenza di modelli"""

    at_bof = zope.interface.Attribute("True se non vi sono elementi precedenti a quello corrente")
    at_eof = zope.interface.Attribute("True se non vi sono elementi successivi a quello corrente")
    is_dirty = zope.interface.Attribute("True se si è in modalità di inserimento o di modifica, vale"
                                        " a dire che l'elemento corrente è potenzialmente cambiato")
    is_new = zope.interface.Attribute("True se si è posizionati su un nuovo record")

    def firstElement():
        "Sposta il focus sul primo elemento"

    def prevElement():
        "Sposta il focus sul primo elemento"

    def nextElement():
        "Sposta il focus sul elemento successivo"

    def lastElement():
        "Sposta il focus sull'ultimo elemento"

    def editElement():
        "Entra in modalità di modifica del elemento corrente"

    def insertElement():
        "Inserisci un nuovo elemento ed entra in modalità di modifica"

    def deleteElement():
        "Cancella il elemento corrente"

    def cancelChanges():
        "Annulla le modifiche apportate al elemento"

    def commitChanges():
        "Conferma le modifiche apportate."

    def search():
        "Entra in modalità di ricerca"


class IModelCursorChangedEvent(zope.component.interfaces.IObjectEvent):
    """Evento scatenato quando un IModelCursor cambia di stato, o posizione"""

class ICommitChangesEvent(zope.component.interfaces.IObjectEvent):
    """Evento che segnala l'avvenuto commit"""