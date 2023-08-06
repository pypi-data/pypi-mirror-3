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

class IListStore(zope.interface.Interface):
    """
    Interfaccia marker per la semantica usata dalle
    InstrumentedLists di SA, che poi è quella della lista
    """

class IObjectAddedEvent(zope.component.interfaces.IObjectEvent):
    """Evento utilizzato dallo store quando viene aggiunto un item"""


class IObjectRemovedEvent(zope.component.interfaces.IObjectEvent):
    """Evento utilizzato dallo store quando viene rimosso un item"""
