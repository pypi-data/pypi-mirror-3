# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import os
import sys
import tempfile
import unittest

class WingPathInformationTest(unittest.TestCase):
    def setUp(self):
        from z3wingdbg.debugger.wingpathinformation import WingPathInformation
        self.utility = WingPathInformation()
        self.tempDir = tempfile.mkdtemp()
        
    def tearDown(self):
        for path, dirnames, filenames in os.walk(self.tempDir, topdown=False):
            for filename in filenames:
                os.remove(os.path.join(path, filename))
            os.rmdir(path)
        
    def testDefaultPath(self):
        # Depends on sys.platform, testing that is pointless as we'd duplicate
        # the code. Instead we test that we get a path back with platform-
        # appropriate path separators
        path = self.utility.platformDefault
        self.assertTrue(len(path) > 0)
        self.assertEqual(path, os.path.join(*os.path.split(path)))
        
    def testSoftwareHomeEmpty(self):
        self.assertEqual(self.utility.softwareHome, None)
        
    def testSoftWareHomeAssignEmptyDir(self):
        def assignValue(val):
            self.utility.softwareHome = val
        self.assertRaises(ValueError, assignValue, self.tempDir)
        
    def testSoftwareHomeSearchSubdirs(self):
        paths = (self.tempDir,)
        if sys.platform.startswith('darwin'):
            paths = (os.path.join(self.tempDir, 'Contents/MacOS'),
                     os.path.join(self.tempDir, 'WingIDE.app/Contents/MacOS'))
        for path in paths:
            for subpath in ('bin', 'src'):
                dir = os.path.join(path, subpath)
                os.makedirs(dir)
                open(os.path.join(dir, 'wingdb.py'), 'w') # touch
        for path in paths:
            self.utility.softwareHome = self.tempDir
            self.assertEqual(self.utility.softwareHome, path)
            os.remove(os.path.join(path, 'bin', 'wingdb.py'))
            self.utility.softwareHome = self.tempDir
            self.assertEqual(self.utility.softwareHome, path)
            os.remove(os.path.join(path, 'src', 'wingdb.py'))
            
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WingPathInformationTest),
        ))

if __name__ == '__main__':
    unittest.main()
