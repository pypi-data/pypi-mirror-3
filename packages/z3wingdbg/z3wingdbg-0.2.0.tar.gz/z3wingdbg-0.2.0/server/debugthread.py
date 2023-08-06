# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from twisted.python.threadpool import ThreadPool

class DebugThread(ThreadPool):
    def __init__(self, debugger):
        self.debugger = debugger
        ThreadPool.__init__(self, minthreads=1, maxthreads=1, 
                            name='z3wingdbg.server.debugthread')
        
    def start(self):
        """Start the thread, and the debugger"""
        ThreadPool.start(self)
        self.callInThread(self.debugger.start)
        
    def stop(self):
        """Stop the debugger, then the thread"""
        self.callInThread(self.debugger.stop)
        ThreadPool.stop(self)
