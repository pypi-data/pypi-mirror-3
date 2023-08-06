# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import thread
import unittest

class TestDebugThread(unittest.TestCase):
    def setUp(self):
        from z3wingdbg.server.debugthread import DebugThread
        self.thread = DebugThread(None)
        
    def testStartStop(self):
        class DummyDebugger(object):
            started = False
            stopped = False 
            def start(self):
                self.started = True
            def stop(self):
                self.stopped = True
        self.thread.debugger = DummyDebugger()
        self.thread.start()
        self.thread.stop()
        # Stop joins the threads, only then can we be sure that the debugger
        # has been started, then stopped.
        self.assertTrue(self.thread.debugger.started)
        self.assertTrue(self.thread.debugger.stopped)
        
    def testSameThread(self):
        class DummyDebugger(object):
            startid = None
            stopid = None
            def start(self):
                self.startid = thread.get_ident()
            def stop(self):
                self.stopid = thread.get_ident()
        class Callable(object):
            self.id = None
            def __call__(self):
                self.id = thread.get_ident()
        self.thread.debugger = DummyDebugger()
        callable = Callable()
        self.thread.start()
        self.thread.callInThread(callable)
        self.thread.stop()
        self.assertNotEqual(self.thread.debugger.startid, thread.get_ident())
        self.assertEqual(self.thread.debugger.startid,
                         self.thread.debugger.stopid)
        self.assertEqual(self.thread.debugger.startid, callable.id)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDebugThread),
        ))

if __name__ == '__main__':
    unittest.main()

