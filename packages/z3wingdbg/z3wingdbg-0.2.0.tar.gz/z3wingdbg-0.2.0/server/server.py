# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from ZODB.interfaces import IDatabase

from zope import component, event, interface

from zope.app.twisted.server import ZopeTCPServer

from z3wingdbg.interfaces import IDebugServer, DebugServerStartedEvent
from z3wingdbg.interfaces import DebugServerStoppedEvent
from debugthread import DebugThread

class AbstractDebugServer(object):
    interface.implements(IDebugServer)
    
    name = None
    
    _triggerId = None
    
    def __init__(self, host, port, debugger):
        self._thread = DebugThread(debugger)
        
        database = component.getUtility(IDatabase)
        
        self._server = ZopeTCPServer(
            '%s:%s:%s' % (self.name, host, port), port,
            self.factory(database, self._thread), interface=host)
        
        self._thread.start()
        self._server.startService()
        from twisted.internet import reactor
        self._triggerId = reactor.addSystemEventTrigger('before', 'shutdown', 
                                                        self.shutdown)
        event.notify(DebugServerStartedEvent())
        
    def factory(self, database, thread):
        raise NotImplementedError
        
    def shutdown(self):
        from twisted.internet import reactor
        reactor.removeSystemEventTrigger(self._triggerId)
        
        self._server.stopService()
        event.notify(DebugServerStoppedEvent())
        # Stop the debug thread from the main reactor thread to avoid
        # join problems if the server is stopped from the debug thread itself
        reactor.callFromThread(self._thread.stop)
    
    def runInDebugContext(self, callable):
        self._thread.callInThread(callable)
