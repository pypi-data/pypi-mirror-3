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


def DatabaseConfigurator(section):
    """Applica la configurazione proveniente dalla sezione "database".

    Viene richiamato alla lettura della sezione <database> dalla
    configurazione, come impostato nel file `component.xml`::

      <sectiontype name="database"
                   datatype="pypapi.db.config.DatabaseConfigurator">
        <key name="uri" datatype="string" />
      </sectiontype>
    """

    # XXX: è "più corretto" arrivarci comunque tramite getUtility(),
    # posto che qui siamo nello stesso "contesto" e quindi è
    # ragionevole arrivarci direttamente?
    from pypapi.db.db import Database

    Database.URI = section.uri

    return section
