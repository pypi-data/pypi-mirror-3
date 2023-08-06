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


from sqlalchemy import (Boolean, CHAR, Date, DateTime, Integer, Float,
                        SmallInteger, Unicode, UnicodeText, VARCHAR,Time)

boolean_t = Boolean()
cap_t = CHAR(5)
codicefiscale_t = CHAR(16)
date_t = Date()
flag_t = CHAR(1)
integer_t = Integer()
largeid_t = Integer()
longstring_t = Unicode(100)
partitaiva_t = CHAR(11)
pathname_t = VARCHAR(128)
provincia_t = CHAR(2)
remark_t = UnicodeText()
shortstring_t = Unicode(50)
smallid_t = SmallInteger()
smallint_t = SmallInteger()
stringid_t = VARCHAR(15)
timestamp_t = DateTime()
tinystring_t = Unicode(25)
username_t = VARCHAR(15)
url_t = VARCHAR(128)
hash_t = VARCHAR(40)
real_t = Float
catastale_t = VARCHAR(4)
coid_t = VARCHAR(15)
valuta_t = CHAR(3)
contributo_t = CHAR(20)
descrizione_t = VARCHAR(250)
codiceinterno_t = VARCHAR(20)
time_t = Time()

__all__ = ['boolean_t', 'cap_t', 'codicefiscale_t', 'date_t', 'flag_t', 'integer_t',
           'largeid_t', 'longstring_t', 'partitaiva_t', 'pathname_t',
           'provincia_t', 'remark_t', 'shortstring_t', 'smallid_t', 'smallint_t',
           'stringid_t', 'timestamp_t', 'tinystring_t', 'username_t', 'url_t', 'hash_t',
           'real_t', 'catastale_t','coid_t','valuta_t','contributo_t','descrizione_t',
           'codiceinterno_t','time_t']
