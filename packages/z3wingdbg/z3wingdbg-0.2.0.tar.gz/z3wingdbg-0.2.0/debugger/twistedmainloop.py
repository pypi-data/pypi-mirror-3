# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import logging

from twisted.internet.interfaces import IReadDescriptor

from zope import component, interface

from z3wingdbg.interfaces import IWingDebugService

class WingDebuggerClientSocketDescriptor(object):
    """Wrapper around the netserver IDE client connection socket"""
    interface.implements(IReadDescriptor)
    fileno = None
    
    def __init__(self, socket, callback):
        socket.setblocking(0)
        self.socket = socket
        self.fileno = socket.fileno
        self.callback = callback
        self.service = component.getUtility(IWingDebugService)
        self.log = logging.getLogger('z3wingdbg.debugger.twistedmainloop')
        
        from twisted.internet import reactor
        self.reactor = reactor
        self.startReading()

    def startReading(self):
        """Start waiting for read availability."""
        self.reactor.addReader(self)
        
    def stopReading(self):
        """Stop waiting for read availability"""
        self.reactor.removeReader(self)
        
    def logPrefix(self):
        """The select loop calls this on every select to log information"""
        return 'z3wingdbg.debugger.twistedmainloop.socketdescriptor'
    
    def connectionLost(self, *args):
        """Called when twisted reactor shuts down"""
        pass
        
    def close(self):
        del self.socket
        self.stopReading()
        
    def doRead(self):
        if not self.socket:
            return
        # Stop polling until the debug thread has dealt with us
        self.stopReading()
        self.log.debug('Dispatching callback on debugthread')
        self.service.server.runInDebugContext(self.debugThreadCallback)
        
    def debugThreadCallback(self):
        # Called in debug thread. Call callback and resume polling
        if not self.socket:
            return
        self.log.debug('In debug thread, dispatching callback')
        self.callback()
        self.startReading()
        # Wake up the reactor now that we are reading again
        self.reactor.wakeUp()

class WingDebuggerClientSocketHook(object):
    """netserver._extensions._SocketHook implementation
    
    This class integrates the IDE client connection socket into the twisted
    mainloop when asked.
    
    """
    descriptors = None
    
    def __init__(self):
        self.log = logging.getLogger('z3wingdbg.debugger.twistedmainloop')
        self.descriptors = {}
        
    def _Setup(self, ignored, socket, callback):
        """Immediatly register the passed socket"""
        return self._RegisterSocket(socket, callback)
    
    def _RegisterSocket(self, socket, callback):
        self.log.debug(
            'Registering client socket %s, %#x callback with twisted',  
            socket.getsockname(), id(socket))
        descriptor = WingDebuggerClientSocketDescriptor(socket, callback)
        self.descriptors[socket] = descriptor
        return socket
    
    def _UnregisterSocket(self, socket):
        self.log.debug('Removing wrapped socket %#x from twisted' % id(socket))
        descriptor = self.descriptors.get(socket)
        if descriptor:
            del self.descriptors[socket]
            descriptor.close()
    
def handleDebugServerStart(event):
    """Register our sockethook with the debugger"""
    event.service.debugger.setSocketRegistrationHook(
        WingDebuggerClientSocketHook())
