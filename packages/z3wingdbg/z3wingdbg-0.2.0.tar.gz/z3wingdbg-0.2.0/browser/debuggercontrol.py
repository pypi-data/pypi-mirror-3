# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope import component
from zope.publisher.browser import BrowserView

from zope.i18n import MessageFactory

from z3wingdbg.interfaces import IWingDebuggerVersion, IWingDebugService
from z3wingdbg.interfaces import DebugServerStartError, IDEConnectionError

_ = MessageFactory('z3wingdbg')

class ControlView(BrowserView):
    def getService(self):
        return component.getUtility(IWingDebugService)
    
    def getVersion(self):
        version = component.getUtility(IWingDebuggerVersion)
        return version.getWingDebuggerVersion()
        
    def getStatus(self):
        service = self.getService()
        if service.debugServerRunning:
            debugger = dict(
                color='green',
                status=_(u'Started'),
                action='debugger.stop',
                action_label=_(u'Stop Debugger'))
            
            if service.connectedToIDE:
                ide = dict(
                    color='green',
                    status=_(u'Connected'),
                    action='ide.disconnect',
                    action_label=_(u'Disconnect IDE'))
            else:
                ide = dict(
                    color='red',
                    status=_(u'Not connected'),
                    action='ide.connect',
                    action_label=_(u'Connect IDE'))
        else:
            debugger = dict(
                color='red',
                status=_(u'Stopped'),
                action='debugger.start',
                action_label=_(u'Start Debugger'))
            
            ide = dict(
                color='grey',
                status=_(u'No debugger'),
                action='ide.connect',
                action_label=_(u'Connect IDE'),
                disabled=True)
        
        return dict(debugger=debugger, ide=ide)
    
    actions = ('debugger.start', 'debugger.stop', 'ide.connect',
               'ide.disconnect')
        
    def action(self):
        service = self.getService()
        for action in self.actions:
            if action in self.request:
                return getattr(self, action.replace('.', '_'))(service)
        
    def debugger_start(self, service):
        if service.debugServerRunning:
            return _(u'The server is already running')
        try:
            service.startDebugServer()
        except (DebugServerStartError, IDEConnectionError), exception:
            return exception.args[0]
        return _(u'Debugger started')
    
    def debugger_stop(self, service):
        if not service.debugServerRunning:
            return _(u'The server is not running')
        service.stopDebugServer()
        return _(u'Debugger stopped')
        
    def ide_connect(self, service):
        if service.connectedToIDE:
            return _(u'The debugger is already connected to the IDE')
        try:
            service.connectIDE()
        except IDEConnectionError, exception:
            return exception.args[0]
        return _(u'Connected to IDE')
        
    def ide_disconnect(self, service):
        if not service.connectedToIDE:
            return _(u'The debugger is not connected to the IDE')
        service.disconnectIDE()
        return _(u'Disconnected the IDE')
