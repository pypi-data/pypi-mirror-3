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


class IWorkFlow(zope.interface.Interface):

    uri = zope.interface.Attribute(u"XPDL files path")


class IProcess(zope.interface.Interface):
    """Entity can handle a process"""


class IWorkFlowForm(zope.interface.Interface):
    """Process management form"""

