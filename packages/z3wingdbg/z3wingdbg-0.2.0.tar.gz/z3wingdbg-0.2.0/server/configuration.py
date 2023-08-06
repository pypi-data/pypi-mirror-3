# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from persistent import Persistent
from zope import interface, component

from zope.app.container import constraints

from z3wingdbg.interfaces import IWingConfiguration, IDebugServerConfiguration

class IDebugServerConfigurationContained(interface.Interface):
    constraints.containers(IWingConfiguration)
    
class DebugServerConfiguration(Persistent):
    interface.implements(IDebugServerConfiguration,
                         IDebugServerConfigurationContained)
    
    host = u'localhost'
    port = None
