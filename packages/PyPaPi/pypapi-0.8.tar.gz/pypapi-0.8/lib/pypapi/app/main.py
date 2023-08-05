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


import logging, os, sys
import ZConfig
from pkg_resources import resource_filename
from zope.component import getUtility
from pypapi.db.interfaces import IDatabase, ILibraryName

def main(workhorse, schemafile=None, configfile=None):
    """Main Entry Point.

    Funzione generica che inizializza e carica la configurazione e il
    sottosistema di logging.

    `workhorse` è un *callable* che implementa le funzionalità specifiche.
    Viene eseguito passandogli la configurazione letta come unico parametro.
    """

    from optparse import OptionParser
    from pypapi import __version__

    parser = OptionParser(usage="%prog [opzioni] [config-name=value...]",
                          version="PyPaPi " + __version__)
    parser.add_option("-c", "--config-file", dest="configfile",
                      help="Usa il FILE specificato come configurazione",
                      metavar="FILE")
    parser.add_option("-s", "--schema-file", dest="schemafile",
                      help="Usa il FILE specificato come schema di configurazione",
                      metavar="FILE")

    options, args = parser.parse_args()

    if options.schemafile is not None:
        schemafile = options.schemafile
    elif schemafile is None:
        schemafile = os.path.join(os.path.dirname(__file__), "schema.xml")

    try:
        schema = ZConfig.loadSchema(schemafile)
    except Exception, e:
        print "Errore nello schema di configurazione %r: %s" % (schemafile, str(e))
        sys.exit(1)

    if options.configfile is not None:
        configfile = options.configfile
    elif configfile is None:
        # cerco nella libreria un conf con lo stesso nome
        library_name = getUtility(ILibraryName)
        configfile = resource_filename(library_name, '%s.conf'%library_name)
        #configfile = os.path.join(os.path.dirname(__file__), "basic.conf")

    try:
        config, handlers = ZConfig.loadConfig(schema, configfile, args)
    except Exception, e:
        print "Errore nella configurazione %r: %s" % (configfile, str(e))
        sys.exit(2)

    # configura il logging: SOLO dopo questo passo è possibile utilizzare
    # il logging.
    config.eventlog()
    for logger in config.loggers:
        logger()
    logging.debug("Configurazione base effettuata: schema=%r, config=%r",
                  schemafile, configfile)

    logging.debug('Lancio il workhorse')
    try:
        exit_status = workhorse(config)
    except:
        exit_status = 255
        logging.critical("Un errore ha impedito la corretta esecuzione dell'applicazione",
                         exc_info=True)
    else:
        logging.debug('Esecuzione completata')

    sys.exit(exit_status)


if __name__ == '__main__':
    def workhorse(config):
        logging.debug("Config: %s", config)
        logging.debug("Forms: %s", [f.uifile for f in config.application.forms])

    main(workhorse)
