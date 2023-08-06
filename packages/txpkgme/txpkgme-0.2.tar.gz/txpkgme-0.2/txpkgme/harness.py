# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Harness that can send and receive requests to a pkgme-service.
"""

from twisted.internet import defer, reactor as mod_reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.error import TimeoutError
from twisted.python.failure import Failure
from twisted.protocols.policies import (
    ProtocolWrapper,
    WrappingFactory,
    )
from twisted.web.resource import Resource
from twisted.web.server import Site

from pkgme_service_client.client import build_package

from .utils import parse_json


class CallbackResource(Resource):
    """A Twisted web resource that waits for a POST."""

    def __init__(self, on_post, reactor):
        """A web resource that fires a Deferred on POST.

        :param on_post: A function that will be called when a POST request is
            received. Will be fired with a tuple containing the request method
            and body.
        """
        Resource.__init__(self)
        self.on_post = on_post
        self.reactor = reactor

    def render(self, request):
        # This means that the first request to this resource will be treated
        # as the actual callback request. I'm not sure if we're providing an
        # accurate double if we just assume the first hit is the real
        # thing. -- jml
        method = request.method
        body = request.content.getvalue()
        # If we shut down immediately, the response never gets sent.  Sadly,
        # Twisted doesn't seem to have an event for when the response is sent,
        # so we do the best we can by waiting for this cycle of the event loop
        # to finish, and thus the request to be sent.
        def shutdown():
            self.on_post((method, body))
        self.reactor.callLater(0.1, shutdown)
        return '<html></html>'


class NotifyOnConnectionLost(ProtocolWrapper):

    def __init__(self, factory, wrappedProtocol):
        ProtocolWrapper.__init__(self, factory, wrappedProtocol)
        self.connectionLostDeferred = defer.Deferred()

    def connectionLost(self, reason):
        ProtocolWrapper.connectionLost(self, reason)
        if self.connectionLostDeferred:
            d, self.connectionLostDeferred = self.connectionLostDeferred, None
            d.callback(None)


class DisconnectAllOnStopListening(WrappingFactory):

    protocol = NotifyOnConnectionLost

    def __init__(self, disconnectedDeferred, wrappedFactory):
        WrappingFactory.__init__(self, wrappedFactory)
        self.disconnectedDeferred = disconnectedDeferred

    def doStop(self):
        WrappingFactory.doStop(self)
        d = defer.gatherResults(
            [p.connectionLostDeferred for p in self.protocols])
        d.chainDeferred(self.disconnectedDeferred)


class WebServer(object):

    def __init__(self, reactor=None, timeout=60, hostname='localhost',
                 port=0, clock=None):
        if reactor is None:
            reactor = mod_reactor
        self.reactor = reactor
        if clock is None:
            clock = self.reactor
        self.clock = clock
        # The length of time to wait for hearing back from pkgme-service.
        self.timeout = timeout
        self._hostname = hostname
        self._port = port
        self._clear_state()

    def _clear_state(self, passthrough=None):
        self._disconnected = None
        self._listening_port = None
        self._on_callback = None
        return passthrough

    def _run_web_server(self, root):
        endpoint = TCP4ServerEndpoint(self.reactor, self._port)
        self._disconnected = defer.Deferred()
        site = DisconnectAllOnStopListening(self._disconnected, Site(root))
        d = endpoint.listen(site)
        def web_server_up(listening_port):
            self._listening_port = listening_port
            address = listening_port.getHost()
            return 'http://%s:%s' % (self._hostname, address.port)
        return d.addCallback(web_server_up)

    def make_root_resource(self, deferred):
        """Create a root resource with URLs for everything pkgme will need.

        The created resource has a callback node, an errback node

        XXX: Better docstring

        :return: An ``IResource`` and a dict to the relative URLs from keys
            that the pkgme-service will expect the URLs at.
        """
        metadata_urls = {}
        root = Resource()
        root.putChild(
            'callback', CallbackResource(deferred.callback, self.clock))
        metadata_urls['callback_url'] = 'callback'
        root.putChild(
            'errback', CallbackResource(deferred.errback, self.clock))
        metadata_urls['errback_url'] = 'errback'
        return root, metadata_urls

    def run(self):
        self._on_callback = defer.Deferred()
        root, metadata_urls = self.make_root_resource(self._on_callback)
        d = self._run_web_server(root)
        d.addCallback(lambda x: (x, metadata_urls))
        def server_up((url, metadata_urls)):
            update_urls(url, metadata_urls)
            return root, url, metadata_urls
        d.addCallback(server_up)
        return d

    def set_timeout(self, d, seconds):
        """Fire 'd' with TimeoutError if it isn't fired in 'seconds' time."""
        timeout_call = self.clock.callLater(
            seconds, d.errback, TimeoutError())
        def cancel_timeout(ignored):
            if timeout_call.active():
                timeout_call.cancel()
            return ignored
        d.addBoth(cancel_timeout)
        return d

    def shut_down_web_server(self, passthrough=None):
        d = self._listening_port.stopListening()
        # We are only properly shut down when the port has stopped
        # listening and when all the clients have disconnected.
        d = defer.gatherResults([self._disconnected, d])
        return d.addCallback(lambda x: self._clear_state(passthrough))

    def send_api_request(self, metadata, pkgme_service_root):
        build_package(pkgme_service_root, metadata)
        # Fire the on_callback Deferred with an error if we don't get
        # anything back from the celery task -- a very likely failure
        # mode. This gives the test framework time to do clean up.
        self.set_timeout(self._on_callback, self.timeout)
        return self._on_callback


def update_urls(base_url, url_dict):
    for key, value in url_dict.items():
        if isinstance(value, dict):
            update_urls(base_url, value)
        else:
            url_dict[key] = '%s/%s' % (base_url, value)


class PkgmeServiceError(Exception):
    """Raised on error from a remote pkgme-service."""

    def __init__(self, body):
        error = None
        try:
            body = parse_json(body)
        except ValueError:
            traceback = "Non-JSON response"
        else:
            error = body.pop('error', None)
            if error:
                try:
                    traceback = error.pop('traceback', 'No traceback')
                except AttributeError:
                    traceback = error
                    error = None
            else:
                traceback = 'No traceback'
        self.body = body
        self.traceback = traceback
        self.error = error


def wrap_pkgme_service_error(failure):
    try:
        method, json_body = failure.value
    except ValueError:
        return failure
    return Failure(PkgmeServiceError(json_body))
