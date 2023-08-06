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


from datetime import datetime, date
import time
from PyQt4 import QtCore

class VariantConverter(object):

    double_type_template = 'from_%s_to_%s'
    single_type_template = 'to_%s'

    def __init__(self, variant):

        self.context = variant
        self.qtype = variant.typeName

    def convert(self, py_type, *args, **kw):

        py_type = py_type.__name__
        double_type_method = self.double_type_template % (py_type, self.qtype)
        method = getattr(self, double_type_method, None)
        if method is not None:
            return method(*args, **kw)
        single_type_method = self.single_type_template % py_type
        method = getattr(self, single_type_method, None)
        if method is not None:
            return method(*args, **kw)
        raise TypeError("Conversione da %s a %s non supportata" % (self.qtype, py_type))

    __call__ = convert

    def to_str(self, encoding=None):

        if encoding is not None:
            uni = self.to_unicode()
            return uni.encode(encoding)
        else:
            return str(self.context.toString())

    __str__ = to_str

    def to_unicode(self):

        return unicode(self.context.toString())

    __unicode__ = to_unicode

    def to_bool(self):

        return self.context.toBool()

    __nonzero__ = to_bool

    def to_int(self):

        value = self.context.toInt()
        if value[1] is False:
            raise ValueError("Il valore non può essere convertito in intero")
        return value[0]

    __int__ = to_int

    def to_float(self):

        value = self.context.toDouble()
        if value[1] is False:
            raise ValueError("Il valore non può essere convertito in float")
        return value[0]

    __float__ = to_float

    def to_ascii(self):

        return self.to_str('ascii')

    def to_datetime(self):
        if self.context.type() == QtCore.QVariant.String:
            try:
                t = time.strptime(self.context.toString(), '%d/%m/%Y')
                yyyy = t.tm_year
                M = t.tm_mon
                d = t.tm_mday
                h = t.tm_hour
                m = t.tm_min
            except ValueError:
                return None
        else:
            value = self.context.toDateTime()
            date_part = value.date()
            time_part = value.time()
            yyyy, M, d = date_part.year(), date_part.month(), date_part.day()
            h, m = time_part.hour(), time_part.minute()
        new_value = datetime(yyyy, M, d, h, m)
        return new_value

    def to_time(self):
        if self.context.type() == QtCore.QVariant.Time:
            t = self.context.toTime()
            new_value = t.toPyTime()
        else:
            raise ValueError("Il valore non può essere convertito in un time")

        return new_value

#    def to_date(self):
#        date_part = self.context.toDateTime().date()
#        yyyy, M, d = date_part.year(), date_part.month(), date_part.day()
#        new_value = date(yyyy, M, d)
#        return new_value

