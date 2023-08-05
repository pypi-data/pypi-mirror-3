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
from zope import schema

EXPAND, COLLAPSE = range(2)

class IEntitaBase(zope.interface.Interface):

    caption = schema.TextLine(title=u" ",
                              description=u"Etichetta di default",)

    caption.setTaggedValue('layout', EXPAND)

    limit = schema.Int(title=u"Limit",
                       description=u"Numero massimo di entità da estrarre"
                                   u"nelle ricerche filtrate.")
    limit.setTaggedValue('default', 1000)

    readonly = schema.Bool(title=u"Read only",
                           description=u"L'entità è in modalità sola lettura")

    def getCaption():
        "Etichetta dell'entità"
