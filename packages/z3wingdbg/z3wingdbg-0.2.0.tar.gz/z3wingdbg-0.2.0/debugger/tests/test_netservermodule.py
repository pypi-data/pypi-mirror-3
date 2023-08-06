# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import os
import sys
import tempfile
import unittest

from zope import component
from zope.app.testing import placelesssetup

from z3wingdbg.interfaces import IWingPathInformation

dummyWingDBModule = """\
class DummyDbgTracer(object):
    called = False
    
    def set_always_stop_excepts(self, *args):
        self.called = True
    def set_never_stop_excepts(self, *args):
        self.called = True
        
class DummyDbgServer(object):
    def __init__(self):
        self.dbgtracer = DummyDbgTracer()

class DummyNetServer(object):
    def __init__(self, path):
        self.path = path
        self.dbgserver = DummyDbgServer()

def FindNetServerModule(path):
    return DummyNetServer(path)
"""

class DummyPathInfo(object):
    softwareHome = None

class NetServerModuleTest(unittest.TestCase):
    def setUp(self):
        placelesssetup.setUp()
        self.tempDir = tempfile.mkdtemp()
        self.pathinfo = DummyPathInfo()
        component.provideUtility(self.pathinfo, IWingPathInformation)
        from z3wingdbg.debugger.netservermodule import NetServerModule
        self.utility = NetServerModule()
        
    def tearDown(self):
        for path, dirnames, filenames in os.walk(self.tempDir, topdown=False):
            for filename in filenames:
                os.remove(os.path.join(path, filename))
            os.rmdir(path)
        placelesssetup.tearDown()
        
    def _createDummyModule(self, path):
        os.makedirs(path)
        modulefile = open(os.path.join(path, 'wingdb.py'), 'w')
        modulefile.write(dummyWingDBModule)
        modulefile.close()
        
    def testNoPath(self):
        self.assertRaises(ImportError, lambda: self.utility.netserver)
        
    def testNoModule(self):
        self.pathinfo = self.tempDir
        self.assertRaises(ImportError, lambda: self.utility.netserver)
        
    def testBinImport(self):
        path = self.tempDir
        self._createDummyModule(os.path.join(path, 'bin'))
        self.pathinfo.softwareHome = path
        netserver = self.utility.netserver
        self.assertEqual(netserver.path, path)
        
    def testSrcImport(self):
        path = self.tempDir
        self._createDummyModule(os.path.join(path, 'src'))
        self.pathinfo.softwareHome = path
        netserver = self.utility.netserver
        self.assertEqual(netserver.path, path)
        
    def testChangePath(self):
        path = os.path.join(self.tempDir, 'foo')
        self._createDummyModule(os.path.join(path, 'bin'))
        self.pathinfo.softwareHome = path
        netserverFoo = self.utility.netserver
        
        path = os.path.join(self.tempDir, 'bar')
        self._createDummyModule(os.path.join(path, 'bin'))
        self.pathinfo.softwareHome = path
        netserverBar = self.utility.netserver
        
        self.assertEqual(netserverBar.path, path)
        self.assertTrue(netserverFoo.dbgserver.dbgtracer.called)
            
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(NetServerModuleTest),
        ))

if __name__ == '__main__':
    unittest.main()
