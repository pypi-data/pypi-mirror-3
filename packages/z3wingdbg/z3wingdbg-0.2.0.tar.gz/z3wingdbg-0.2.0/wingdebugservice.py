# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import logging
import time

from ZODB.interfaces import IDatabase
from zope import component, event, interface
from zope.i18n import MessageFactory

from zope.app.appsetup.appsetup import getConfigContext
from zope.app.component.hooks import getSite
from zope.app.publication.zopepublication import ZopePublication

from interfaces import IWingDebugService, IWingConfiguration
from interfaces import IDebugServerConfiguration, INetworkDebuggerFactory
from interfaces import IDebugServerFactory, DebugServerStartError
from interfaces import IDEConnectionError, IDEConnectedEvent
from interfaces import IDEDisconnectedEvent

_ = MessageFactory('z3wingdbg')

class WingDebugService(object):
    interface.implements(IWingDebugService)
    
    server = None
    debugger = None
    
    def startDebugServer(self, context=None):
        if self.debugServerRunning:
            return
        
        if context is None:
            context = getSite()
        
        config = component.getUtility(IWingConfiguration, context=context)
        serverconfig = component.queryUtility(IDebugServerConfiguration,
                                              config.serverType, 
                                              context=context)
        
        if not serverconfig:
            raise DebugServerStartError(
                _(u'debugserver-config-not-found',
                  u'Could not find any configuration for the ${serverType} '
                  u'debug server', dict(serverType=config.serverType)))
        
        debuggerFactory = component.getUtility(INetworkDebuggerFactory)
        serverFactory = component.queryUtility(IDebugServerFactory, 
                                               config.serverType)
        if not serverFactory:
            raise DebugServerStartError(
                _(u'debugserver-factory-not-found',
                  u'Could not find a factory for the ${serverType} '
                  u'debug server', dict(serverType=config.serverType)))
        
        try:
            self.debugger = debuggerFactory(config)
        except (ValueError, ImportError):
            raise DebugServerStartError(_(
                u'winghome-incorrect',
                u'The Wing debug libraries could not be loaded, please verify '
                u'your configured Wing Home'))
        
        self.server = serverFactory(serverconfig, self.debugger)
        
        if config.autoConnect:
            self.connectIDE()
    
    def stopDebugServer(self):
        if not self.debugServerRunning:
            return
        self.server.shutdown()
        self.server = self.debugger = None
    
    @property
    def debugServerRunning(self):
        return self.server is not None
    
    def connectIDE(self):
        if not self.debugServerRunning or self.connectedToIDE:
            return
        
        connected = []
        def connectClient():
            self.debugger.connectClient()
            connected.append(self.debugger.clientConnected)
        self.server.runInDebugContext(connectClient)
        
        # time out the call, up to 5 seconds
        timeout = time.time() + 5
        while time.time() < timeout and not connected:
            time.sleep(0.05)
        if not connected or not connected[0]:
            message = _(u'ide-connection-failure',
                        u'Failed to connect to the IDE. Check your IDE host '
                        u'and port are correct.')
            if not connected:
                message = _(u'ide-connection-timeout',
                            u'Connection to IDE timed out')
            raise IDEConnectionError(message)
        else:
            event.notify(IDEConnectedEvent())
    
    def disconnectIDE(self):
        if not (self.debugServerRunning and self.connectedToIDE):
            return
        # Call disconnect from the current thread. Not entirely thread-safe,
        # but with multiple calls to disconnectClient, we at the worst get
        # exceptions from an already cleared __fChannel.
        try:
            self.debugger.disconnectClient()
        except:
            pass
        else:
            event.notify(IDEDisconnectedEvent())
    
    @property
    def connectedToIDE(self):
        return self.debugger is not None and self.debugger.clientConnected
    
WingDebugServiceUtility = WingDebugService()

def handleProcessStart(event):
    """Start the Wing Debug Server at startup if so configured"""
    # Open a context
    database = component.getUtility(IDatabase)
    connection = database.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    log = logging.getLogger('z3wingdbg.wingdebugservice')
    
    try:
        if root_folder is None:
            return
        
        debugmode = getConfigContext().hasFeature('devmode')
        if not debugmode:
            return
        
        config = component.queryUtility(IWingConfiguration, 
                                        context=root_folder)
        if not config:
            return
        
        if not config.autoStart:
            return
        
        if config.attachPort is not None:
            log.warn('Not autostarting the wing debug server when allowing '
                     'remote connections.')
            return
        
        service = component.getUtility(IWingDebugService)
        try:
            service.startDebugServer(context=root_folder)
        except (DebugServerStartError, IDEConnectionError):
            pass
    finally:
        connection.close()
