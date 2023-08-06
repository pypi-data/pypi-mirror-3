import os
# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import sys

from zope import interface
from zope.cachedescriptors import property

from z3wingdbg.classproperty import classproperty
from z3wingdbg.interfaces import IWingPathInformation

_searchPaths = ('bin', 'src')
_darwinPaths = ('Contents/MacOS', 'WingIDE.app/Contents/MacOS')

def _wingDebugModulePath(softwareHome):
    """Return a valid Wing software home containing wingdb.py, or None"""
    # On Mac OSX, the path needs to be extended into user-hidden directories
    if sys.platform.startswith('darwin'):
        for extra in _darwinPaths:
            internal = os.path.join(softwareHome, extra)
            for path in _searchPaths:
                if os.path.isfile(os.path.join(internal, path, 'wingdb.py')):
                    return internal
    else:
        for path in _searchPaths:
            if os.path.isfile(os.path.join(softwareHome, path, 'wingdb.py')):
                return softwareHome

class WingPathInformation(object):
    interface.implements(IWingPathInformation)
    
    _softwareHome = None
    
    @property.Lazy
    def platformDefault(self):
        if sys.platform == 'win32':
            return ur'c:\Program Files\Wing IDE 2.1'
        elif sys.platform.startswith('darwin'):
            return u'/Applications/WingIDE.app/Contents/MacOS'
        else:
            return u'/usr/lib/wingide2.1'
        
    class softwareHome(classproperty):
        def __get__(self):
            return self._softwareHome
        
        def __set__(self, softwareHome):
            if not os.path.isdir(softwareHome):
                raise ValueError('Not a directory')
            
            softwareHome = _wingDebugModulePath(softwareHome)
            if not softwareHome:
                raise ValueError('Not a Wing installation, wingdb.py not found')
                
            self._softwareHome = softwareHome
            
WingPathInformationUtility = WingPathInformation()
