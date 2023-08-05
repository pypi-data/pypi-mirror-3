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


from zope.interface import Interface
from db import *
from storage import *
from base import *
from permission import *


class IORM(zope.interface.interfaces.IInterface):
    """
    Interfaccia "tipo" che identifica le interfacce che
    costituiscono l'api di accesso al database.
    """


class ILibraryName(Interface):
    """
    Marca posto per l'utility library name, ovverlo la lista dei nomi
    (o il nome singolo) delle applicazioni PyPaPi da cui
    inizializzare le entità.
    """

class IAuthentication(Interface):
    """
    Marca post per l'utility che registra la codifica base64 dell'autenticazione
    """
