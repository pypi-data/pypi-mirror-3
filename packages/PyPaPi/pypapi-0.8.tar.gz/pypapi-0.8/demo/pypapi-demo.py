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

from zope.component import provideUtility, getMultiAdapter
from pypapi.app.main import main
from pypapi.db.interfaces import ILibraryName
from pypapi.db.db import createDatabase
from pypapi.db.storage import SAListStore
from pypapi.db.source.interfaces import IDbSource
from pypapi.db.model import metadata
from pypapi.ui.cute.interfaces import IForm
from pypapi.ui.cute.search import addSearchHelperFor
from pypapi.ui.cute.validator import addValidatorsFor
from pypapi.ui.widgets.navigationbar import addAdminToolBars
from pypapi.app.forms import connectDb, connectCm, connectWf
from pypapidemo.db import interfaces
from pypapidemo.db.model import entities
from pypapi.cm.cm import createContentManagement
from pypapi.wf.wf import createWorkFlow
from pypapi.lang import installTranslator

def demoData():
    s = db.session
    a1 = entities.Author(name=u"Tarun J", surname=u"Tejpal")
    g1 = entities.Genre(description=u"Comedy")
    g2 = entities.Genre(description=u"Romance")
    g3 = entities.Genre(description=u"Thriller")
    b1 = entities.Book(isbn=u"978-88-11-68102-1",
                       title=u"L'alchimia del desiderio",
                       description=u"Passione, esotismo, erotismo, slittamenti spazio-temporali, "
                                   u"prosa brillante. L''esordio di uno dei piu'' affascinanti "
                                   u"uomini dell''India moderna.",
                       author=a1,
                       genre=g2)
    s.add_all([a1, g1, g2, g3, b1])
    s.flush()
    

def application(config):
    from PyQt4.QtGui import QApplication

    app = QApplication([])

    installTranslator(app)

    connectDb(config, None, None)
    connectCm(config, None, None)
    connectWf(config)

    # create db (if not exists)
    if len(db.engine.table_names()) == 0:
        metadata.create_all(db.engine)
        demoData()

    result = True

    source = IDbSource(interfaces.IBook)
    store = SAListStore(source)
    form = getMultiAdapter((store, None), IForm, 'books')
    addSearchHelperFor(form)
    addValidatorsFor(form)
    addAdminToolBars(form)
    form.edit(0)
    form.show()

    result = app.exec_()
    return not result and 1 or 0

# register appication demo
provideUtility('pypapidemo', provides=ILibraryName)

# create db, content management, and workflow utilities
db = createDatabase()
cm = createContentManagement()
wf = createWorkFlow()

try:
    main(application)
finally:
    if db.ready:
        db.close()
