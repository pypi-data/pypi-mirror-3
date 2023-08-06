# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope import interface
import zope.traversing.interfaces
from zope.location import Location
from zope.security.checker import ProxyFactory, NamesChecker

class IDebuggerControl(interface.Interface):
    """Wing Debugger Control views location"""

class DebuggerControl(Location):

    interface.implements(IDebuggerControl)

debuggerControllerRoot = Location()
interface.directlyProvides(
    debuggerControllerRoot,
    zope.traversing.interfaces.IContainmentRoot,
    )
debuggerControllerRoot = ProxyFactory(debuggerControllerRoot,
                                      NamesChecker("__class__"))

debuggerController = DebuggerControl()
debuggerController.__parent__ = debuggerControllerRoot
debuggerController.__name__ = '++wing++debugger'
