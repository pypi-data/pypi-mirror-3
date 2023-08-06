# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope import interface
from zope.traversing.interfaces import ITraversable, TraversalError

class WingNamespace(object):
    """A ++wing++ namespace to hang debugger control views of"""
    interface.implements(ITraversable)
    
    def __init__(self, context, request):
        self.context = context
        
    def traverse(self, name, ignored):
        if name == 'debugger':
            import debuggercontrol
            return debuggercontrol.debuggerController
        raise TraversalError(self.context, name)
