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

import logging
import os,sys
import base64
from logging import getLogger
from PyQt4 import QtCore, QtGui
import zope.interface
from zope.component.interfaces import ComponentLookupError
from zope.component import adapter, getMultiAdapter, getUtility, \
     provideUtility, queryUtility, provideAdapter
from zope.event import notify
from sqlalchemy.exc import InvalidRequestError, InternalError, IntegrityError, ProgrammingError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import object_session
from pypapi.cm.interfaces import IFolder
from pypapi.db.interfaces import IDatabase, IAuthentication, ILibraryName, IPermission
from pypapi.db.source.interfaces import IDbSource, IDbSourceFactory
from pypapi.db.storage import SAListStore
from pypapi.db.util import initDbSources
from pypapi.cm.interfaces import IContentManagement
from pypapi.wf.interfaces import IWorkFlow, IWorkFlowForm
from pypapi.wf.forms import WorkFlowForm
from pypapi.ui.cute.interfaces import IDataContext, IPyPaPiForm, IForm,\
     IWidgetCreationEvent, IStoreEditForm, ISelectForm, ICommitChangesEvent, \
     IMainWindow, IPyPaPiDialog, IWidgetLayoutController, ISelectFormLite, IModel
from pypapi.ui.cute.event import provideHandler, IndexChangedEvent
from pypapi.ui.cute.search import addSearchHelperFor, searchWindowModalPreview
from pypapi.ui.cute.validator import addValidatorsFor
import pypapi.ui.resources
import pypapi.app
from pypapi.app.pyconsole import ConsoleForm
from pypapi.ui.widgets.navigationbar import addAdminToolBars
from pypapi.ui.widgets.pickerdialog import PickerDialog, PickerDialogLite


logger = getLogger('app')


def get_user_name():
    """Ritorna il nome dell'utente loggato al sistema.

    Se per qualche motivo non può essere determinato, viene restituito None.
    """

    import os, sys

    username = None

    try:
        if sys.platform == 'win32':
            # Ricetta adattata da bzrlib/win32utils.py
            try:
                import ctypes
            except ImportError:
                pass
            else:
                try:
                    advapi32 = ctypes.windll.advapi32
                    GetUserName = getattr(advapi32, 'GetUserNameW')
                except AttributeError:
                    pass
                else:
                    buf = ctypes.create_unicode_buffer(256+1)
                    n = ctypes.c_int(256+1)
                    if GetUserName(buf, ctypes.byref(n)):
                        username = buf.value
        else:
            import pwd
            username = pwd.getpwuid(os.getuid())[0]
    except:
        # oh well...
        pass

    if username is None:
        # come ultima spiaggia...
        username = os.environ.get('USERNAME', None)

    return username


def connectDb(config, username, password):
    db = getUtility(IDatabase)
    uri = db.URI % dict(username=username, password=password)
    # Nota: non stampo l'uri per non mostrare la password
    logging.debug('Attivo la connessione al database %s', db.URI)
    db.open(uri)
    try:
        db.engine.connect()
    except:
        QtGui.QApplication.beep()
        msg = "Impossibile accedere al database con utente '%s'" % username
        logging.critical(msg)
        info = QtGui.QMessageBox.warning(None, u"Errore", msg, QtGui.QMessageBox.Ok)
        db.close()
        exit()
    authentication = base64.encodestring('%s:%s' % (username or '', password or ''))[:-1]
    provideUtility(authentication, provides=IAuthentication)


def connectCm(config, username, password):
    cm = getUtility(IContentManagement)
    cm.open(config.contentmanagement.uri)
    cm.wrapper.folder_path = config.contentmanagement.folder_path
    cm.wrapper.base_file = config.contentmanagement.base_file
    cm.wrapper.base_folder = config.contentmanagement.base_folder


def connectWf(config):
    wf = getUtility(IWorkFlow)
    wf.open(config.workflow.uri)


class LogOnDialog(QtGui.QDialog):
    """Presenta un dialog per il logon al database."""

    def __init__(self, config, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.config = config

        self.user_label = QtGui.QLabel("Utente")
        self.user_edit = QtGui.QLineEdit()
        self.user_label.setBuddy(self.user_edit)
        username = get_user_name()
        if username is not None:
            self.user_edit.setText(username)
        else:
            username = ''

        grid_layout = QtGui.QGridLayout()

        grid_layout.addWidget(self.user_label, 0, 0)
        grid_layout.addWidget(self.user_edit, 0, 1)

        self.password_label = QtGui.QLabel("Password")
        self.password_edit = QtGui.QLineEdit()
        self.password_label.setBuddy(self.password_edit)
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)

        grid_layout.addWidget(self.password_label, 1, 0)
        grid_layout.addWidget(self.password_edit, 1, 1)

        self.login_button = QtGui.QPushButton("Login")
        self.login_button.setDefault(True)

        self.cancel_button = QtGui.QPushButton("Annulla")

        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)

        icon = QtGui.QIcon(':/images/pypapi.png')
        self.info_button = info_button = QtGui.QPushButton(self)
        info_button.setIconSize(QtCore.QSize(100,100))
        info_button.setIcon(icon)
        info_button.setFixedHeight(100)
        info_button.setFlat(True)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(info_button)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.connect(self.cancel_button, QtCore.SIGNAL("clicked()"), self.abort)
        self.connect(self.login_button, QtCore.SIGNAL("clicked()"), self.authenticate)
        self.connect(self.info_button,  QtCore.SIGNAL("clicked()"), self.about)

        self.setWindowTitle('PyPaPi - Login')
        self.user_edit.setFocus()
        self.user_edit.setSelection(0, len(username))

    def about(self):
        "Mostra delle informazioni sull'applicazione"

        from pypapi import __doc__, __version__

        QtGui.QMessageBox.about(self, "Informazioni su PyPaPi, versione %s" % __version__,
                                __doc__)

    def abort(self):
        "Chiudi il dialog, senza effettuare l'autenticazione"
        self.reject()

    def authenticate(self):
        "Esegui l'autenticazione, se viene superata chiudi il dialog"

        username = str(self.user_edit.text())
        password = str(self.password_edit.text())
        connectDb(self.config, username, password)
        self.accept()


class MainWindow(QtGui.QMainWindow):
    """Form principale dell'applicazione."""

    zope.interface.implements(IMainWindow)

    def __init__(self, config, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.is_admin = False
        if config.application.admin is True:
            self.is_admin = True
        self.setup(config)
        provideHandler(self.decorateForm)
        self.showDefaultForms(config)
        x, y, w, h = eval(config.application.geometry)
        self.setGeometry(x, y, w, h)
        if config.application.maximized is True:
            self.showMaximized()


    def about(self):
        "Mostra delle informazioni sull'applicazione"

        from pypapi import __doc__, __version__

        QtGui.QMessageBox.about(self, "Informazioni su PyPaPi, versione %s" % __version__,
                                __doc__)

    def close(self):
        title = 'Conferma uscita'
        msg = 'Vuoi uscire da PyPaPi?'
        confirm = QtGui.QMessageBox.question(None, title, msg,
                                             QtGui.QMessageBox.Yes,
                                             QtGui.QMessageBox.No)
        if confirm == QtGui.QMessageBox.Yes:
            return QtGui.QMainWindow.close(self)


    def setup(self, config):
        "Esegui il setup della maschera, creando le azioni, i menu e le toolbar."

        self.createCommonActions()
        self.createTaskActions(config)
        self.createMenus()
        if len(self.dock_names)>1:
            self.createDockBars()  # new style
        else:
            self.createToolBars()  # old style
        self.updateMenus()

        self.setWindowTitle(config.application.title)


    def createCommonActions(self):
        "Crea le action comuni, di uscita e di informazioni."

        self.exit_action = QtGui.QAction("Es&ci", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Esci dall'applicazione")
        self.connect(self.exit_action, QtCore.SIGNAL("triggered()"), self.close)

        self.about_action = QtGui.QAction(self.tr("&Info"), self)
        self.about_action.setStatusTip(self.tr("Mostra le informazioni sull'applicazione"))
        self.connect(self.about_action, QtCore.SIGNAL("triggered()"), self.about)


    def createMenus(self):
        "Crea i menu."

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exit_action)

        self.taskMenu = self.menuBar().addMenu("&Moduli")
        for action in self.task_actions['generale']:
            self.taskMenu.addAction(action)

        self.utilityMenu = self.menuBar().addMenu(self.trUtf8("&Utilità"))
        self.createOtherMenus()

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("Aiuto")
        self.helpMenu.addAction(self.about_action)

    def createOtherMenus(self):
        "Hook per le sottoclassi"

    def updateMenus(self):
        "Aggiorna lo stato dei menu"

    def showDefaultForms(self, config):
        """Mostra le form da aprire all'apertura dell'applicazione, e ricerca l'eventuale
        elemento indicato dalla primarykey in config"""
        for f in config.application.forms:
            if f.show:
                class_name = f.form_class.__name__
                form_action = [a for a in self.task_actions['generale'] if a.form_class.__name__==class_name][0]
                form_action.activate(form_action.Trigger)
                if f.filter is not None:
                    form = self.centralWidget().currentSubWindow().widget()
                    pdc = IDataContext(form)
                    db = getUtility(IDatabase)
                    source = db.createNewSession().query(pdc.current_entity.__class__).filter(f.filter).all()
                    form.store = SAListStore(source, disable_session=True)
                    form.edit(0)

    def createToolBars(self):
        "Crea le toolbar"

        self.taskToolBar = QtGui.QToolBar("Tasks")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.taskToolBar)
        self.taskToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.taskToolBar.setIconSize(QtCore.QSize(40, 40))
        for action in self.task_actions['generale']:
            self.taskToolBar.addAction(action)
        self.taskToolBar.setAllowedAreas(QtCore.Qt.LeftToolBarArea)
        self.taskToolBar.setMovable(False)


    def createDockBars(self):
        "Crea la dock bar"

        self.taskDockWidget = QtGui.QDockWidget("Tasks")
        self.taskDockWidget.setFeatures(self.taskDockWidget.NoDockWidgetFeatures)
        self.taskDockWidget.setMinimumWidth(140)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.taskDockWidget)
        toolbox = QtGui.QToolBox()
        self.taskDockWidget.setWidget(toolbox)
        for k in self.dock_names:
            w = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            w.setLayout(layout)
            toolbox.addItem(w, k)
            for action in self.task_actions[k]:
                tb = QtGui.QToolButton(w)
                tb.setMinimumSize(QtCore.QSize(140, 50))
                tb.setIconSize(QtCore.QSize(40, 40))
                tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
                tb.setDefaultAction(action)
                layout.addWidget(tb)
            layout.addStretch()
        self.taskDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.taskDockWidget.setFloating(False)


    def createTaskActions(self, config):
        "Crea le azioni corrispondenti a ciascuna form"

        def createAction(form, group_name='generale'):
            if form.toplevel:
                action = QtGui.QAction(form.getSectionName(), self)
                if (form.menubaricontext != ''):
                    action.setIconText(form.menubaricontext)
                action.setStatusTip(form.title)
                action.form_registration = form.form_registration
                action.form_class = form.form_class
                action.setIcon(QtGui.QIcon(form.icon))
                action.show_search = form.show_search

                self.task_actions[group_name].append(action)
                self.connect(action, QtCore.SIGNAL("triggered()"), self.runTask)

        self.task_actions = {'generale':[]}
        self.dock_names = ['generale',]
        for form in config.application.forms:
            createAction(form)
        for group in config.application.groups:
            group_name = group.getSectionName()
            self.task_actions[group_name] = []
            self.dock_names.append(group_name)
            for form in group.forms:
                createAction(form, group_name)


    def runTask(self):
        """Esegui un certo task, mostrandone la form associata."""
        per = queryUtility(IPermission)
        action = self.sender()
        interface = action.form_registration.form_class.interface
        can_select, _, _, _ = per.resolvePermissions(interface)
        if not can_select:
            msg = 'Non disponi delle autorizzazione per aprire la maschera richiesta'
            logging.debug(msg)
            info = QtGui.QMessageBox.warning(None, u"Accesso negato", msg, QtGui.QMessageBox.Ok)
            return
        if not hasattr(action, "form"):
            form = self.createForm(action)
            if form is None:
                return
        if self.is_admin is True:
            addAdminToolBars(form)
        self.showForm(form)


    def createForm(self, action):
        """Crea la form associata alla action."""

        logging.debug("Creo e imposto la form %r", action.form_class)

        form_name = str(action.text())
        form_source = str(action.form_registration.form_source)

        try:
            # verifico se è stata preparata una sorgente da utilizzare
            # come superset
            #factory = queryUtility(IDbSourceFactory, form_name)
            factory = queryUtility(IDbSourceFactory, form_source)
            if factory is not None:
                db = getUtility(IDatabase)
                session = db.createNewSession()
                source = factory(session)
            # se non è disponibile, creo una sorgente che restituisca
            # tutti i dati disponibili
            else:
                source = IDbSource(action.form_registration.form_class.interface)
            store = SAListStore(source)
            # aggancio alla stessa session i DbSources necessari
            initDbSources(source.query.session)
        except Exception, e:
            logging.error("Impossibile ottenere lo store di base della form", exc_info=True)
            QtGui.QMessageBox.warning(self, "Errore nella configurazione della maschera",
                                      "Impossibile creare la form richiesta:\n%s" % str(e),
                                      QtGui.QMessageBox.Abort)
            return

        try:
            if action.show_search is True:
                form = searchWindowModalPreview(source, form_name)
            else:
                #form = getMultiAdapter((store, None), IForm, form_name)
                form = getMultiAdapter((store,None), IForm, form_source)
            if form is not None:
                form.edit(0)
        except Exception, e:
            logging.error("Impossibile creare la form", exc_info=True)
            QtGui.QMessageBox.warning(self, "Errore nella preparazione della maschera",
                                      "Impossibile creare la form richiesta:\n%s" % str(e),
                                      QtGui.QMessageBox.Abort)
            return

        return form

    @adapter(IStoreEditForm, IWidgetCreationEvent)
    def decorateForm(self, form, event=None):
        """Decora la form con i servizi di base, alla sua creazione."""

        if isinstance(form, QtGui.QMainWindow):
            addSearchHelperFor(form)
        addValidatorsFor(form)


    def showForm(self, form):
        """Mostra la form associata alla action specificata."""

        form.show()


class MdiMainWindow(MainWindow):
    "Versione MDI della finestra principale"

    def setup(self, config):
        "Crea innanzitutto la QMdiArea, poi procedi come al solito."

        self.createWorkspace()
        MainWindow.setup(self, config)
        if len(config.application.icon)>0:
            self.setWindowIcon(QtGui.QIcon(config.application.icon))
        provideHandler(self.createMDIWindow)


    def createWorkspace(self):
        "Crea il workspace in una configurazione MDI"

        self.workspace = QtGui.QMdiArea(self)
        self.setCentralWidget(self.workspace)

        self.connect(self.workspace, QtCore.SIGNAL("subWindowActivated(QMdiSubWindow *)"),
                     self.updateMenus)
        self.window_mapper = QtCore.QSignalMapper(self)
        self.connect(self.window_mapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace.setActiveSubWindow)

    def closeEvent(self, event):
        "Alla chiusura della window principale, chiudi tutte le finestre child"

        db = getUtility(IDatabase)
        if len(db.session.dirty)>0:
            strs = ['%s: %s' % (e.__class__.__name__, e.caption) for e in db.session.dirty]
            if len(strs)>12:
                altri_n = len(strs)-10
                strs = strs[:10]
                strs.append('e altri %d...' % altri_n)
            msg = 'Vuoi salvare le modifiche a questi oggetti prima di uscire?\n\n'
            msg += '\n'.join(strs)
            title = 'Uscita da PyPaPi'
            confirm = QtGui.QMessageBox.question(None, title, msg, QtGui.QMessageBox.Yes,
                                                 QtGui.QMessageBox.No,
                                                 QtGui.QMessageBox.Cancel)
            if confirm == QtGui.QMessageBox.Cancel:
                event.ignore()
                return
            elif confirm == QtGui.QMessageBox.Yes:
                db.session.flush()
            else:
                db.session.expunge_all()

        self.workspace.closeAllSubWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            event.accept()

    def updateMenus(self):
        "Aggiorna lo stato dei menu"

        MainWindow.updateMenus(self)

        hasMdiChild = (self.activeMdiChild() is not None)
        self.close_action.setEnabled(hasMdiChild)
        self.close_all_action.setEnabled(hasMdiChild)
        self.tile_action.setEnabled(hasMdiChild)
        self.cascade_action.setEnabled(hasMdiChild)
        self.next_action.setEnabled(hasMdiChild)
        self.previous_action.setEnabled(hasMdiChild)
        self.separator_action.setVisible(hasMdiChild)

    def updateWindowMenu(self):
        "Ricrea il menu delle window"

        self.windowMenu.clear()
        self.windowMenu.addAction(self.close_action)
        self.windowMenu.addAction(self.close_all_action)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tile_action)
        self.windowMenu.addAction(self.cascade_action)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.next_action)
        self.windowMenu.addAction(self.previous_action)
        self.windowMenu.addAction(self.separator_action)

        windows = self.workspace.subWindowList()

        self.separator_action.setVisible(len(windows) != 0)

        for child in windows:
            action = self.windowMenu.addAction(child.windowTitle())
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.window_mapper, QtCore.SLOT("map()"))
            self.window_mapper.setMapping(action, child)

    def activeMdiChild(self):
        "Ritorna il child attivo, in una configurazione MDI"

        return self.workspace.activeSubWindow()

    def createCommonActions(self):
        "Crea le action comuni"

        MainWindow.createCommonActions(self)
        self.createMDICommonActions()

    def createMDICommonActions(self):

        self.close_action = QtGui.QAction("Chiudi", self)
        self.close_action.setShortcut("Ctrl+F4")
        self.close_action.setStatusTip("Chiudi la finestra attiva")
        self.connect(self.close_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveSubWindow)

        self.close_all_action = QtGui.QAction("Chiudi &tutte", self)
        self.close_all_action.setStatusTip("Chiudi tutte le finestre")
        self.connect(self.close_all_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllSubWindows)

        self.tile_action = QtGui.QAction("Allinea", self)
        self.tile_action.setStatusTip("Allinea le finestre")
        self.connect(self.tile_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.tileSubWindows)

        self.cascade_action = QtGui.QAction("&Cascata", self)
        self.cascade_action.setStatusTip("Disponi le finestre in cascata")
        self.connect(self.cascade_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascadeSubWindows)

        self.next_action = QtGui.QAction("&Successiva", self)
        self.next_action.setShortcut("Ctrl+F6")
        self.next_action.setStatusTip("Sposta il focus alla finestra successiva")
        self.connect(self.next_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextSubWindow)

        self.previous_action = QtGui.QAction("&Precedente", self)
        self.previous_action.setShortcut("Ctrl+Shift+F6")
        self.previous_action.setStatusTip("Sposta il focus alla finestra precedente")
        self.connect(self.previous_action, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousSubWindow)

        self.separator_action = QtGui.QAction(self)
        self.separator_action.setSeparator(True)

    def createOtherMenus(self):
        self.windowMenu = self.menuBar().addMenu("&Finestre")
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

    def createForm(self, action):
        form = MainWindow.createForm(self, action)
        return form

    @adapter(IStoreEditForm, IWidgetCreationEvent)
    def createMDIWindow(self, form, event=None):
        if isinstance(form, QtGui.QMainWindow):
            self.workspace.addSubWindow(form)

    def showForm(self, form):
        """Mostra la form. Se è la prima, allora la mostra massimizzata,
        altrimenti in base allo stato della MDIMain"""
        if len(self.workspace.subWindowList()) > 1:
            form.show()
        else:
            form.showMaximized()
        form.setFocus(QtCore.Qt.OtherFocusReason)


class WidgetLayoutController(object):
    """
    Un utility per la gestione del layout dei widget, come ad esempio lo stato
    di abilitazione.
    """

    zope.interface.implements(IWidgetLayoutController)

    def __init__(self, form):
        self.form = form

    def updateEnabledWidgets(self):
        """
        Gestisce lo stato enabled/diabled dei widget, sulla base del metodo
        personalizzato getWidgetStatus (proprietà widget_status)
        """
        for k, v in self.form.widgets_status.items():
            try:
                from pypapi.ui.widgets.pickerentity import PickerEntity
                widget = getattr(self.form, k)
                if isinstance(widget, QtGui.QLineEdit):
                    widget.setEnabled(v)
                elif isinstance(widget, PickerEntity):
                    widget.setEnabled(v)
                elif isinstance(widget, QtGui.QGroupBox):
                    widget.setEnabled(v)
                elif (hasattr(widget, "setEnabled")) and (type(v) == type(True)) :
                    widget.setEnabled(v)
                else:
                    print 5*'*'
                    print 'Il widget %s non ha il metodo %s'%(widget.objectName(),'setEnabled')
                    print 'e il valore è: %s %s'%(type(v),str(v))
                    print 5*'*'
            except:
                pass


@adapter(IPyPaPiForm)
@zope.interface.implementer(IWidgetLayoutController)
def pyPaPiForm2widgetLayoutController(form):
    wlc = WidgetLayoutController(form)
    return wlc
provideAdapter(pyPaPiForm2widgetLayoutController)

@adapter(IPyPaPiDialog)
@zope.interface.implementer(IWidgetLayoutController)
def pyPaPiDialog2widgetLayoutController(form):
    wlc = WidgetLayoutController(form)
    return wlc
provideAdapter(pyPaPiDialog2widgetLayoutController)


class PyPaPiDialog(QtGui.QDialog):
    """
    La classe base delle dialog
    """

    zope.interface.implements(IPyPaPiDialog)

    def __init__(self, store, parent, first=False):
        QtGui.QDialog.__init__(self, parent)
        self.initForm()
        self.store = store
        self.accept_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return))
        self.connect(self.accept_button, QtCore.SIGNAL('clicked()'), self.acceptEvent)
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'), self.cancelEvent)
        if hasattr(self, 'info_button'):
            self.connect(self.info_button, QtCore.SIGNAL('clicked()'), self.info)

        pdc = IDataContext(self)
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.indexChanged)
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.updateWidgetsLayout)
        self.first = first

    def _getFirst(self):
        return self._first
    def _setFirst(self, mode):
        if mode is True:
            self.accept_button.setIcon(QtGui.QIcon(":/icons/add.png"))
        else:
            self.accept_button.setIcon(QtGui.QIcon(":/icons/accept.png"))
        self._first = mode
    first = property(_getFirst, _setFirst)

    def initToolBars(self):
        "Non inserire le toolbar standard."
        pass

    def acceptEvent(self):
        dc = IDataContext(self)
        dc.commitChanges()
        self.accept()

    def cancelEvent(self):
        self.reject()

    def indexChanged(self, row):
        pass

    def info(self):
        "Mostra un dialog con le informazioni"
        entityInfo(IDataContext(self).current_entity).exec_()

    def reject(self):
        if self.first:
            self.first = False
        dc = IDataContext(self)
        dc.cancelChanges()
        QtGui.QDialog.reject(self)

    def updateWidgetsLayout(self):
        wlc = IWidgetLayoutController(self)
        wlc.updateEnabledWidgets()

    def getWidgetsStatus(self):
        return {}
    widgets_status = property(lambda self: self.getWidgetsStatus())


class PyPaPiForm(QtGui.QMainWindow):
    """
    La classe base PyPaPiForm implementa tutte le funzionalità
    specifiche delle applicazioni PyPaPi, che non si vogliono rendere
    nel framework
    """

    zope.interface.implements(IPyPaPiForm)

    def __init__(self, store, parent):

        QtGui.QMainWindow.__init__(self, parent)
        self.initForm()
        self.store = store
        pdc = IDataContext(self)
        provideUtility(self, IForm, pdc.name)
        if len(self.store) == 0:
            # XXX: unica possibilità la creazione di un nuovo elemento?
            self.centralWidget().setEnabled(False)
            self.no_elements = True
        else:
            self.no_elements = False
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.indexChanged)
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.updateTitle)
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'), self.updateWidgetsLayout)
        self.connect(pdc.mapper, QtCore.SIGNAL('currentIndexChanged(int)'),
                     lambda i: self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor)))

    @adapter(IPyPaPiForm, ICommitChangesEvent)
    def refresh(self):
        pass

    def insertElement(self):
        pdc = IDataContext(self)
        if self.no_elements is True:
            self.centralWidget().setEnabled(True)
            self.no_elements = False
        pdc.insertElement()

    def cancelChanges(self):
        pdc = IDataContext(self)
        pdc.cancelChanges()

    def commitChanges(self):
        pdc = IDataContext(self)
        pdc.commitChanges()

    def flushChanges(self):
        pdc = IDataContext(self)
        pdc.flushChanges()
        pdc.refresh()

    def updateTitle(self):
        "Mostra nel titolo l'indice e il numero di record"
        oldt = str(self.windowTitle().split('(')[0]).strip()
        idx = IDataContext(self).current_index
        t = '%s (%d di %d)' % (oldt, idx+1, len(self.store))
        self.setWindowTitle(t)

    def updateWidgetsLayout(self):
        wlc = IWidgetLayoutController(self)
        wlc.updateEnabledWidgets()

    def getWidgetsStatus(self):
        return {}
    widgets_status = property(lambda self: self.getWidgetsStatus())

    def indexChanged(self, row):
        pass

    def info(self):
        "Mostra un dialog con le informazioni"
        dlg = entityInfo(IDataContext(self).current_entity)
        dlg.exec_()

    def container(self):
        """
        Mostra i file 'contenuti'
        """
        cm = getUtility(IContentManagement)
        cm.openFolder(IDataContext(self).current_entity.folder_path)

    def workflow(self):
        """
        Open the process form
        """
        form = IWorkFlowForm(self)
        form.show()

    def admin(self):
        '''
        Apre una form con una console Python
        '''
        pyconsole = ConsoleForm(locals= locals(),parent = self)
        pyconsole.show()

    def quickSearch(self, _id, on_key=None):
        """
        Execute a quick search of the element with key _id.
        If on_key is None, primary key will be used.
        """
        pdc = IDataContext(self)
        entity = pdc.current_entity
        session = object_session(entity)
        if on_key is None:
            new_entity = session.query(entity.__class__).get(_id)
        else:
            try:
                new_entity = session.query(entity.__class__).filter_by(**{on_key:_id}).one()
            except NoResultFound:
                new_entity = None
        return new_entity


@adapter(IForm)
@zope.interface.implementer(IWorkFlowForm)
def form2workflowForm(form):
    wff = WorkFlowForm(parent=form)
    return wff
provideAdapter(form2workflowForm)


def entityInfo(entity, detail=False):
    "Mostra un dialog con le informazioni"
    if not hasattr(entity, 'rec_creato'):
        msg = 'Informazioni non presenti'
    else:
        creato_da = entity.rec_creato_da or '-'
        creato = entity.rec_creato and entity.rec_creato.strftime('%d/%m/%Y %H:%M')
        modificato_da = entity.rec_modificato_da or '-'
        modificato = entity.rec_modificato and entity.rec_modificato.strftime('%d/%m/%Y %H:%M') or '-'
        msg  = 'Creazione:\t %s (%s)\n' % (creato, creato_da)
        msg += 'Modifica:\t %s (%s)\n' % (modificato, modificato_da)
    session = object_session(entity)
    extra = u'session:\t %s (%s)\n' % (session, id(session))
    for obj in object_session(entity):
        extra += u'%s\n' % obj
    msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                               'Informazioni',
                                msg,
                                QtGui.QMessageBox.Ok)
    if detail is True:
        msgbox.setDetailedText(extra)
    return msgbox


# zope.schema.Choice
@adapter(IDbSource)
@zope.interface.implementer(ISelectForm)
def source2SelectForm(source):
    root_interface = source.getItemInterface()
    pd = PickerDialog(False, source=source, interface=root_interface)
    return pd
provideAdapter(source2SelectForm)

@adapter(IDbSource)
@zope.interface.implementer(ISelectFormLite)
def source2SelectFormLite(source):
    root_interface = source.getItemInterface()
    pd = PickerDialogLite(False, source=source, interface=root_interface)
    return pd
provideAdapter(source2SelectFormLite)


# zope.schema.List
@adapter(IModel)
@zope.interface.implementer(ISelectForm)
def model2SelectForm(model):
    pd = PickerDialog()
    return pd
provideAdapter(model2SelectForm)