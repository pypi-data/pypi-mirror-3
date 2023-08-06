# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope.app.appsetup.bootstrap import ensureUtility

from z3wingdbg.interfaces import IWingConfiguration
from z3wingdbg.configuration import WingConfiguration, ensureConfiguration
from z3wingdbg.generations import getRootFolder
from z3wingdbg.server.configuration import DebugServerConfiguration

def evolve(context):
    """Create configuration utility if not yet present"""

    root_folder = getRootFolder(context)

    ensureUtility(root_folder, IWingConfiguration, 'WingConfiguration', 
                  WingConfiguration, asObject=True)
    
    ensureConfiguration(root_folder, u'http', DebugServerConfiguration,
                        port=50080)
