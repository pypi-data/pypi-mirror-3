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


from pypapi.ui.widgets.nullabledateedit import NullableDateEdit
from zope.interface import implements
from zope.component import provideHandler, adapter
from pypapi.ui.cute import interfaces, widget

# XXX: da sistemare o eliminare

class NullableDateTimeEdit(NullableDateEdit):

    implements(interfaces.INullableDateTimeEditWidget)


@adapter(interfaces.INullableDateTimeEditWidget, interfaces.IWidgetCreationEvent)
def nullableDateTimeEditWidgetBinding(data_widget, event):

    dc = interfaces.IDataContext(data_widget)
    col_index = widget.resolveColumn(data_widget, dc)[0]
    dc.mapper.addMapping(data_widget, col_index, 'text')

provideHandler(nullableDateTimeEditWidgetBinding)
