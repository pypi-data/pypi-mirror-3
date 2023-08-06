# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from twisted.web2 import log, server, wsgi
from twisted.web2.channel.http import HTTPChannel, HTTPFactory

from zope import component, interface

from zope.app.wsgi import WSGIPublisherApplication
from zope.app.twisted.http import Prebuffer

from z3wingdbg.interfaces import IDebugServerFactory
from server import AbstractDebugServer

# The HTTP server is basically the same as the regular Zope HTTP server. The
# two differences are:
#
# - Limit the HTTP Channel to process only one request at a time
# - Run the WSGIHandler on our debug thread instead of in the reactor threadpool

class DebugThreadWSGIResource(wsgi.WSGIResource):
    """Render WSGI on the debug thread"""
    def __init__(self, application, thread):
        self._thread = thread
        super(DebugThreadWSGIResource, self).__init__(application)
    
    def renderHTTP(self, ctx):
        handler = wsgi.WSGIHandler(self.application, ctx)
        d = handler.responseDeferred
        # Run it in the debug thread
        self._thread.callInThread(handler.run)
        return d
    
class LimitedHTTPChannel(HTTPChannel):
    """HTTP Channel processing only one request at a time"""
    maxPipeline = 1
    
class HTTPDebugServer(AbstractDebugServer):
    name = 'z3wingdbg.http'
    
    def factory(self, database, thread):
        resource = DebugThreadWSGIResource(WSGIPublisherApplication(database),
                                           thread)
        resource = log.LogWrapperResource(resource)
        resource = Prebuffer(resource)

        factory = HTTPFactory(server.Site(resource))
        factory.protocol = LimitedHTTPChannel    
        return factory
    
def createHTTPDebugServer(config, debugger):
    return HTTPDebugServer(config.host, config.port, debugger)

factory = component.factory.Factory(
    createHTTPDebugServer, interfaces=interface.implementedBy(HTTPDebugServer))
interface.alsoProvides(factory, IDebugServerFactory)
