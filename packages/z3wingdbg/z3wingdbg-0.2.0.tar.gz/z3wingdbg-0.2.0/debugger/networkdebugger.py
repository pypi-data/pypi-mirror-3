# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import logging
import os

from zope import component, interface
from zope.i18n import MessageFactory

from z3wingdbg.interfaces import INetworkDebugger, INetworkDebuggerFactory
from z3wingdbg.interfaces import IWingPathInformation, DebugServerStartError
from z3wingdbg.interfaces import PWD_PROFILE, PWD_PATH, PWD_MANUAL
from netservermodule import INetServerModule

_ = MessageFactory('z3wingdbg')

class LogWrapper(object):
    """Wrapper around the standard logging module for Wing NetworkServer
    
    Strips subsystem and datestamp from written lines (log module already
    provides these) and logs lines with DEBUG severity
    
    """
    _data = ''

    def __init__(self):
        self._logger = logging.getLogger('z3wingdbg.debugger.networkdebugger')
        
    def _strip(self, line):
        # Lines are of the form "wingdb - Y/m/d H:M:S - log info"; discard
        # everything before the second ' - '
        return line.split(' - ', 3)[-1]
        
    def write(self, text):
        self._data += text
        while '\n' in self._data:
            line, self._data = self._data.split('\n', 1)
            self._logger.debug(self._strip(line))

class NetworkDebugger(object):
    """Network Debugger implementation
    
    Simple wrapper around netserver.CNetworkServer
    
    """
    interface.implements(INetworkDebugger)
    
    _networkserver = None
    
    def __init__(self, wing_home, host, port, attachport, pwsource=PWD_PROFILE,
                 pwpath=None, pw=None):
        pathinfo = component.getUtility(IWingPathInformation)
        nsmodule = component.getUtility(INetServerModule)
        pathinfo.softwareHome = wing_home
        netserver = nsmodule.netserver
        
        if netserver.dbgserver.dbgtracer.get_tracing():
            raise DebugServerStartError(
                _(u'Another debugger is already active. Wing currently only '
                  u'supports one active debugger per process.'))
        
        attach = -1
        pwdir = (netserver.abstract.kPWFilePathUserProfileDir,)
        pwfile = '.wingdebugpw'
        if attachport is not None:
            attach = attachport
            if pwsource == PWD_PATH:
                if not os.path.exists(pwpath or ''):
                    raise DebugServerStartError(
                        _(u'No valid password source path specified'))
                if os.path.isfile(pwpath):
                    pwpath, pwfile = os.path.split(pwpath)
                pwdir = (pwpath,)
            
        logger = netserver.abstract.CErrStream((LogWrapper(),))
        server = netserver.CNetworkServer(
            host, port, attach, logger, pwfile_path=pwdir, pwfile_name=pwfile)
        
        if attachport is None or pwsource == PWD_MANUAL:
            # netserver insists we set a non-empty string, but only uses
            # the password for verifying incoming attachment requests.
            password = (pwsource != PWD_MANUAL) and 'ignored' or pw
            server.SetSecurityInfo(
                netserver.abstract.securechannel.kNoEncryption, password)
            
        if attachport is not None and not server.IsSecurityInfoValid():
            raise DebugServerStartError(
                _(u'No valid password source was provided, please check your '
                  u'configuration'))
            
        # We set our own sockethook later
        server.SetUseSocketHooksOnImport(False)
        
        self._networkserver = server
        
    def connectClient(self):
        self._networkserver.ConnectToClient()
    
    def disconnectClient(self):
        # This appears naughty: we call a private method. This is pretty 
        # harmless though, you can also disconnect from the client side, which
        # results in the same method being called.
        self._networkserver._CNetworkServer__CloseChannel()
    
    @property
    def clientConnected(self):
        return not self._networkserver.ChannelClosed()
    
    def start(self):
        self._networkserver.StartDebug(connect=False)
    
    def stop(self):
        self._networkserver.StopDebug()
        
    def setSocketRegistrationHook(self, hook):
        self._networkserver.SetSocketRegHook(hook)
        
def createDebugger(config):
    return NetworkDebugger(config.wingHome, config.ideHost, config.idePort,
                           config.attachPort, config.attachPasswordSource,
                           config.attachPasswordPath, config.attachPassword)

factory = component.factory.Factory(
    createDebugger, interfaces=interface.implementedBy(NetworkDebugger))
interface.alsoProvides(factory, INetworkDebuggerFactory)
