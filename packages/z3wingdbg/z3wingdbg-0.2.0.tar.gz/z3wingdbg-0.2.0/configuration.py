# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope import interface, component

from zope.app.container.btree import BTreeContainer
from zope.app.container import constraints

from interfaces import IWingConfiguration, IDebugServerConfiguration
from interfaces import IWingPathInformation, PWD_PROFILE, PWD_PATH, PWD_MANUAL

class IDebugServerConfigurationContainer(interface.Interface):
    constraints.contains(IDebugServerConfiguration)
    
class WingConfiguration(BTreeContainer):
    interface.implements(IWingConfiguration, 
                         IDebugServerConfigurationContainer)
    
    def __init__(self):
        super(WingConfiguration, self).__init__()
        pathinfo = component.getUtility(IWingPathInformation)
        self.wingHome = pathinfo.platformDefault
   
    wingHome = u''
    
    ideHost = u'localhost'
    idePort = 50005
    
    serverType = u'http'
    
    autoStart = False
    autoConnect = True
    
    attachPort = None
    attachPasswordSource = PWD_PROFILE
    attachPasswordPath = None
    attachPassword = None

def ensureConfiguration(root_folder, serverType, factory, 
                        interface=IDebugServerConfiguration, **kw):
    """Add a debug server configuration to the wing configuration

    Returns the added configuration object, or None
    
    """
    config = component.getUtility(IWingConfiguration, context=root_folder)
    if serverType in config:
        return None
    serverConfig = factory()
    config[serverType] = serverConfig
    root_folder.getSiteManager().registerUtility(serverConfig, interface, 
                                                 serverType)
    serverConfig = config[serverType]
    for k, v in kw.iteritems():
        setattr(serverConfig, k, v)
    return serverConfig

