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

from PyQt4 import QtGui
from logging import getLogger
from zope.component import adapts
from zope.interface import implements
from zope.wfmc.interfaces import IActivity, IParticipant, IWorkItem
from zope.wfmc.attributeintegration import AttributeIntegration

logger = getLogger('wf')

class BaseApplication(object):
    """Base class for the WorkFlow applications."""

    adapts(IParticipant)
    implements(IWorkItem)

    def __init__(self, participant):
        self.participant = participant

    def start(self):
        pass

    def finish(self):
        pass

    def _exec(self):
        pass


class AutoFinish(BaseApplication):
    """A basic 'auto finish' WorkFlow application."""

    def start(self):
        #self.participant.activity.workItemFinished(self)
        pass


class ManualFinish(BaseApplication):
    """A basic 'manual finish' WorkFlow application."""

    def finish(self):
        pd = self.participant.activity.process.definition
        aid = self.participant.activity.activity_definition_identifier
        activity = pd.activities[aid]
        msg = activity.description
        confirm = QtGui.QMessageBox.question(None, u"Workitem", msg,
                                              QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if confirm == QtGui.QMessageBox.Yes:
            self.participant.activity.workItemFinished(self)


class GenericParticipant(object):
    """
    A generic participant (not defined in xpdl file)
    """
    adapts(IActivity)
    implements(IParticipant)

    def __init__(self, activity):
        self.activity = activity


def bindIntegration(pd):
    """
    Bind the AttributeIntegration to the process definition.
    """

    integration = AttributeIntegration()
    for k in pd.applications.keys():
        application = globals()[k]
        setattr(integration, '%sWorkItem' % k, application)

    # participants in xpdl file
    for k in pd.participants.keys():
        participant_class = pd.participants[k].__class__
        # bind activity property
        def initParticipant(self, name):
            self.activity = name
        setattr(participant_class, '__init__', initParticipant)
        setattr(integration, '%sParticipant' % k, participant_class)
        logger.debug('Setup %s participant.' % k)

    # generic participant
    integration.Participant = GenericParticipant
    logger.debug('Setup generic participant.')
    pd.integration = integration