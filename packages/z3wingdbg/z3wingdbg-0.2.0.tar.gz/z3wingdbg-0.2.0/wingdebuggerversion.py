# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import os.path

from zope import interface
from zope.app.applicationcontrol.zopeversion import ZopeVersion

import z3wingdbg
from interfaces import IWingDebuggerVersion

class WingDebuggerVersion(ZopeVersion):
    interface.implementsOnly(IWingDebuggerVersion)
    
    def __init__(self, path=None):
        if path is None:
            path = os.path.dirname(os.path.abspath(z3wingdbg.__file__))
        super(WingDebuggerVersion, self).__init__(path)
        
    def getWingDebuggerVersion(self):
        # getZopeVersion has been co-opted to return our version string instead
        return self.getZopeVersion()
        
WingDebuggerVersionUtility = WingDebuggerVersion()
