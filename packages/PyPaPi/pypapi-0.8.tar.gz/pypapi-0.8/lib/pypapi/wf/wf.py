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

from os import path
from xml.dom.minidom import parseString
from logging import getLogger
from zope.interface import implements
from zope.component import provideUtility
from zope.wfmc import xpdl, interfaces
from zope.wfmc.process import Process, WorkflowData
from pypapi.wf.interfaces import IWorkFlow
from pypapi.wf.applications import bindIntegration
import pypapi.ui.resources

logger = getLogger('wf')

EXCLUDES = ('CAPTION_TRIM_CHAR', 'CAPTION_TRIM_LENGTH', 'files', 'folder_path')
Y_ACTIVITY_OFFSET = 32
X_ACTIVITY_OFFSET = 2

class WorkFlowProcess(Process):
    """"""

    def __init__(self, definition, start, context=None):
        self.process_definition_identifier = definition.id
        self.startTransition = start
        self.context = context
        self.activities = {}
        self.nextActivityId = 0
        self.workflowRelevantData = WorkflowData()
        self.applicationRelevantData = WorkflowData()
        self._dom = None
        self.offsets = {}


    def transition(self, activity, transitions):
        from_id = self.nextActivityId
        Process.transition(self, activity, transitions)
        to_id = self.nextActivityId
        if activity is not None and to_id != from_id:
            activity_def = self.definition.activities[activity.activity_definition_identifier]
            logger.debug('Activity finished: %s' % activity_def.description)


    def isActive(self):
        return len(self.activities.keys()) > 0
    active = property(isActive)


    def getXpdlSource(self):
        if self._dom is not None:
            return self._dom.toprettyxml()
        return None


    def setXpdlSource(self, source):
        """
        Parsing of the xpdl file to find the offsets of the activities
        """
        dom = parseString(source)
        dom = [n for n in dom.getElementsByTagName('xpdl:WorkflowProcess') if n.getAttribute('Name') == self.process_definition_identifier][0]
        self.offsets = {}
        max_y = {}
        # initial offset
        for node in dom.getElementsByTagName('xpdl:Activity'):
            _id = node.getAttribute('Id')
            for attr in node.getElementsByTagName('xpdl:ExtendedAttribute'):
                if attr.getAttribute('Name') == 'JaWE_GRAPH_PARTICIPANT_ID':
                    participant = attr.getAttribute('Value')
                elif attr.getAttribute('Name') == 'JaWE_GRAPH_OFFSET':
                    x, y = eval(attr.getAttribute('Value'))
            self.offsets[_id] = (participant, x, y)
            if not hasattr(max_y, 'participant'):
                max_y[participant] = y + 66 # activity box height (50) and bottom padding (16)
            max_y[participant] = max(max_y[participant], 150)
        for node in dom.childNodes:
            if node.nodeName == 'xpdl:ExtendedAttributes':
                attributes = [c for c in node.childNodes if c.nodeName == 'xpdl:ExtendedAttribute']
        for attr in attributes:
            name = attr.getAttribute('Name')
            if name in ('JaWE_GRAPH_END_OF_WORKFLOW', 'JaWE_GRAPH_START_OF_WORKFLOW'):
                value = dict([pair.split('=') for pair in attr.getAttribute('Value').split(',')])
                participant = value['JaWE_GRAPH_PARTICIPANT_ID']
                y_offset = int(value['Y_OFFSET']) + 44 # start/end height (32) and padding (12)
                max_y[participant] = max(max_y[participant], y_offset)
            elif name == 'JaWE_GRAPH_WORKFLOW_PARTICIPANT_ORDER':
                par_order = attr.getAttribute('Value').split(';')
        self._dom = dom
        # absolutize y_offsets
        for k in self.offsets.keys():
            participant, x, y = self.offsets[k]
            for par in par_order:
                if par == participant:
                    break
                y += max_y[par]
            self.offsets[k] = participant, x, y

    xpdlsource = property(getXpdlSource, setXpdlSource)


    def getPointFromActivity(self, activity):
        _id = activity.activity_definition_identifier
        participant, x, y = self.offsets[_id]
        return x + X_ACTIVITY_OFFSET, y + Y_ACTIVITY_OFFSET



class WorkFlow(object):
    """WFMC utility"""

    implements(IWorkFlow)


    def __init__(self, uri=None):
        """"""
        self.uri = uri


    def open(self, uri):
        self.uri = uri


    def processDefinitionsFromEntity(self, entity, _id=None):
        """
        Return a list of processes and image filenames avaiable for the passed entity.
        """
        d = {}
        for attr_name in dir(entity):
            if attr_name in EXCLUDES or attr_name[:2] == '__':
                continue
            attr = getattr(entity, attr_name)
            if isinstance(attr, (str, int, float, unicode)):
                d[attr_name] = attr
        d['type'] = entity.__class__.__name__
        xpdl_filename = self.uri % d
        xpdl_foldername = path.dirname(xpdl_filename)
        f = open(xpdl_filename)
        package = xpdl.read(f)
        f.seek(0)
        xpdlsource = f.read()
        f.close()
        pds = []
        for k in package.keys():
            pd = package[k]
            # new __call__ method
            def callMethod(self, context=None):
                wfp = WorkFlowProcess(self, self._start, context)
                wfp.xpdlsource = xpdlsource
                return wfp
            setattr(pd.__class__, '__call__', callMethod)

            jpg_filename = path.join(xpdl_foldername, pd.id + '.jpg')
            if not path.exists(jpg_filename):
                jpg_filename = None
            if _id is not None and pd.id == _id:
                return pd, jpg_filename
            pds.append((pd, jpg_filename))
        return pds


    def createProcess(self, entity, _id):
        """
        Return the process instance from the passed entity, with corresponding id.
        """
        pd, _ = self.processDefinitionsFromEntity(entity, _id)
        bindIntegration(pd)
        provideUtility(pd, name=pd.id)
        proc = pd()
        proc.workflowRelevantData.self = entity
        if not hasattr(entity, 'processes'):
            entity.processes = []
        entity.processes.append(proc)
        return proc


def createWorkFlow(uri=None):
    wf_utility = WorkFlow(uri=uri)
    provideUtility(wf_utility, provides=IWorkFlow)
    return wf_utility