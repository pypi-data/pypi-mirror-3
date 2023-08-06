# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from zope import interface, schema, component
from zope.component.interfaces import IFactory
from zope.i18n import MessageFactory

_ = MessageFactory('z3wingdbg')

# The main debug service
class IWingDebugService(interface.Interface):
    """Debug service manager"""
    
    def startDebugServer():
        """Start the debug server
        
        May throw a DebugServerStartError.
        
        """
        
    def stopDebugServer():
        """Stop the debug server"""
        
    debugServerRunning = interface.Attribute(
        'Boolean flag indicating wether or not the debug server is running')
        
    def connectIDE():
        """Connect the debug server to the IDE
        
        May throw a IDEConnectionError.
        
        """
    
    def disconnectIDE():
        """Disconnect the IDE"""

    connectedToIDE = interface.Attribute(
        'Boolean flag indicating wether or not the debug server is connected '
        'to the IDE')
    
    server = interface.Attribute('The currently running debug server, or None')
    
    debugger = interface.Attribute('The active debugger, or None')
    
# Service exceptions
class DebugServerStartError(Exception):
    """The debug server failed to start"""
    
class IDEConnectionError(Exception):
    """The debugger failed to connect to the IDE"""
    
# The networked debugger
class INetworkDebugger(interface.Interface):
    """The network debug server
    
    This object is actually both a client to the debugger and a server to the 
    remote debug client.

    """
    
    def connectClient():
        """Establish a connection to client if there isn't one already."""
        
    def disconnectClient():
        """Drop connection to client"""
        
    clientConnected = interface.Attribute(
        'Boolean determining if the IDE is connected')
    
    def start():
        """Start the debugger

        Subsequent code in the current thread is under control of the debugger.
        
        """
    
    def stop():
        """Stop the debug session and drop connection to remote client"""
        
# A debug server
class IDebugServer(interface.Interface):
    """A server publishing code under debugger control
    
    Upon creation, the server should run all requests in a debugger context.
    The runInDebugContext method should allow passed-in callables to be run
    within the same context.
    
    The server is responsible for starting and eventually stopping the 
    debugger.
    
    """
    
    def shutdown():
        """Shut down the server"""
        
    def runInDebugContext(callable):
        """Run code in the debugger context"""
        
# Attachment password source types    
PWD_PROFILE, PWD_PATH, PWD_MANUAL = range(3)

# Configuration of the service and debug server
class IWingConfiguration(interface.Interface):
    """Debug service configuration"""
    
    wingHome = schema.TextLine(
        title=_(u'Wing Home'), 
        description=_(u'wing-home-description',
                      u'The directory where Wing IDE is installed on this '
                      u"machine.  This is used to find Wing IDE's debugger "
                      u'support modules.'))
    
    ideHost = schema.TextLine(
        title=_(u'IDE hostname'),
        description=_(u'ide-hostname-description',
                      u'The host where Wing IDE is listening for the debug '
                      u'connection.'),
        default=u'localhost')
    
    idePort = schema.Int(
        title=_(u'IDE port'),
        description=_(u'ide-port-description',
                      u'The port where Wing IDE is listening for the debug '
                      u'connection.'),
        default=50005, 
        min=0, 
        max=65535)
    
    serverType = schema.Choice(
        title=_(u'Debug server type'),
        description=_(u'server-type-description',
                      u'Type of server to use for the debug server'),
        default=u'http', 
        vocabulary=u'z3wingdbg.servertypes')
    
    autoStart = schema.Bool(
        title=_(u'Auto-start debug server'),
        description=_(u'auto-start-description',
                      u'Automatically start the debug server when Zope starts '
                      u'and is running in Developer Mode.'),
        default=False)
    
    autoConnect = schema.Bool(
        title=_(u'Auto-connect IDE'),
        description=_(u'auto-connect-description',
                      u'Automatically try to connect to the IDE when the '
                      u'debug server is started'),
        default=True)
    
    attachPort = schema.Int(
        title=_(u'Attachment port'),
        description=_(u'attach-port-description',
                      u'Optional port where the debugger will listen for '
                      u'incoming connections from the Wing IDE.'),
        default=None,
        min=0,
        max=65535,
        required=False)
    
    @interface.invariant
    def noAutoStartAndAttachPort(obj):
        """Cannot specify both auto-starting and an attachment port"""
        if obj.autoStart and (obj.attachPort is not None):
            raise interface.Invalid(
                _(u'Cannot specify both auto-start and an attachment port'))
    
    attachPasswordSource = schema.Choice(
        title=_(u'Password source'),
        description=_(u'attach-password-source-description',
                      u'Where to source the password information for the '
                      u'attaching IDE'),
        vocabulary=schema.vocabulary.SimpleVocabulary.fromItems((
            (_(u'Wing Profile Directory'), PWD_PROFILE),
            (_(u'Specified path'),         PWD_PATH),
            (_(u'Specified password'),     PWD_MANUAL))),
        default=PWD_PROFILE)
    
    attachPasswordPath = schema.TextLine(
        title=_(u'Password source path'),
        description=_(u'attach-password-path-description',
                      u'The path to a password source file. Can be both a '
                      u'file as well as a directory path; in the latter case '
                      u'the file .wingdebugpw in that directory will be '
                      u'used.'),
        required=False)
    
    attachPassword = schema.BytesLine(
        title=_(u'Attach password'),
        description=_(u'attach-password-description',
                      u'Password to be supplied by attaching IDE'),
        required=False)
    
    @interface.invariant
    def checkAttachPassword(obj):
        """If source is not PWD_PROFILE, the source needs to be specified"""
        if obj.attachPasswordSource == PWD_PATH and not obj.attachPasswordPath:
            raise interface.Invalid(
                _(u'Please specify the path of the password source'))
        elif obj.attachPasswordSource == PWD_MANUAL and not obj.attachPassword:
            raise interface.Invalid(
                _(u'Please specify an attach password'))
    
class IDebugServerConfiguration(interface.Interface):
    """Debug server configuration"""
    
    host = schema.TextLine(
        title=_(u'Host'),
        description=_(u'server-host-description',
                      u'The host where the debugger will listen for requests '
                      u'from your client.'),
        default=u'localhost')
    
    port = schema.Int(
        title=_(u'Port'),
        description=_(u'server-port-description',
                      u'The port where the debugger will listen for requests'),
        min=0, 
        max=65535)
    
# Factories
class INetworkDebuggerFactory(IFactory):
    """Networked debugger factory"""
    
    def __call__(configuration):
        """Create a networked debugger instance"""

class IDebugServerFactory(IFactory):
    """Debug server factory"""
    
    def __call__(configuration, debugger):
        """Create a debug server"""
        
# Utilities
class IWingDebuggerVersion(interface.Interface):
    """Wing Debugger version"""

    def getWingDebuggerVersion():
        """Return a string containing the debugger version (possibly including
           SVN information)"""

class IWingPathInformation(interface.Interface):
    """Wing path information"""
    
    platformDefault = interface.Attribute(
        'Default wingHome value for the current platform')
    
    softwareHome = interface.Attribute(
        'Path to Wing software installation. Raises a ValueError when set '
        'to an invalid path (e.g. not a Wing installation. If set it may '
        'be readjusted to the reflect a platform-specific path.')
    
# Events
class IDebugStateChangedEvent(interface.Interface):
    """Indicates that the debugger states changed."""
    service = interface.Attribute('The debug service')
    
class IDebugServerStartedEvent(IDebugStateChangedEvent):
    """The debug server has started"""
    
class IDebugServerStoppedEvent(IDebugStateChangedEvent):
    """The debug server has been stopped"""
    
class IIDEConnectedEvent(IDebugStateChangedEvent):
    """The debugger connected to the IDE
    
    Note that this event is only fired when the connection is started by the
    Zope3 service, not when the IDE starts the connection.
    
    """
    
class IIDEDisconnectedEvent(IDebugStateChangedEvent):
    """The debugger disconnected from the IDE
    
    Note that this event is only fired when the connection is closed by the
    Zope3 service, not when the IDE closes the connection.
    
    """
    
class DebugStateChangedEvent(object):
    interface.implements(IDebugStateChangedEvent)
    
    def __init__(self):
        self.service = component.getUtility(IWingDebugService)
        
# Generate the rest of the events as simple subclasses
for iface in (IDebugServerStartedEvent, IDebugServerStoppedEvent, 
              IIDEConnectedEvent, IIDEDisconnectedEvent):
    name = iface.__name__[1:]
    klass = type(name, (DebugStateChangedEvent,), {})
    interface.classImplements(klass, iface)
    globals()[name] = klass

# Vocabularies
def getServerTypesVocabulary(context):
    """List all available debug server types"""
    types = component.getUtilitiesFor(IDebugServerFactory)
    return schema.vocabulary.SimpleVocabulary.fromValues(t[0] for t in types)
