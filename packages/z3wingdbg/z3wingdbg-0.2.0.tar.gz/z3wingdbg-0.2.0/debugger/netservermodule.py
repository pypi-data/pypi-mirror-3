# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

import imp
import os
import sys

from zope import interface, component

from z3wingdbg.interfaces import IWingPathInformation

class INetServerModule(interface.Interface):
    """Provide access to the Wing netserver module"""
    
    netserver = interface.Attribute(
        u'The netserver module. May throw an ImportError')
    
class NetServerModule(object):
    interface.implements(INetServerModule)
    
    _importPath = None
    _netserver = None
    
    def _unload(self):
        """Unload netserver module to enable re-import from different path"""
        if self._netserver is not None:
            # Prevent exceptions from being leaked, remove them explicitly
            tracer = self._netserver.dbgserver.dbgtracer
            tracer.set_always_stop_excepts(())
            tracer.set_never_stop_excepts(())
            # We are the only reference; not even sys.modules has one. Just
            # clear ours to have the garbage collector deal with it.
            self._netserver = None
    
    @property
    def netserver(self):
        pathinfo = component.getUtility(IWingPathInformation)
        path = pathinfo.softwareHome or self._importPath
        if path != self._importPath:
            self._unload()
        if not path:
            raise ImportError('No path set to import Wing debug modules')
        
        if self._netserver is None:
            try:
                info = imp.find_module('wingdb', [os.path.join(path, 'bin'),
                                                  os.path.join(path, 'src')])
                wingdb = imp.load_module('wingdb', *info)
                self._netserver = wingdb.FindNetServerModule(path)
            finally:
                if sys.modules.has_key('wingdb'):
                    del sys.modules['wingdb']
            self._importPath = path
            
        return self._netserver
    
NetServerModuleUtility = NetServerModule()
