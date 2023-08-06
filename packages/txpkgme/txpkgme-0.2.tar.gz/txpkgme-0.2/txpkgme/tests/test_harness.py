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

import json
from StringIO import StringIO

from testtools import (
    run_test_with,
    TestCase,
    )
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer
from twisted.internet.error import TimeoutError
from twisted.python.failure import Failure
from twisted.web import server
from twisted.web.client import (
    Agent,
    FileBodyProducer,
    )
from twisted.web.test.test_web import DummyRequest

from txpkgme.harness import (
    CallbackResource,
    PkgmeServiceError,
    WebServer,
    wrap_pkgme_service_error,
)


class DummyPostRequest(DummyRequest):

    method = 'POST'

    def __init__(self, postpath, content='', session=None):
        DummyRequest.__init__(self, postpath, session=session)
        self.content = StringIO(content)


class CallbackResourceTests(TestCase):

    def _render(self, resource, request):
        result = resource.render(request)
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return defer.succeed(None)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return defer.succeed(None)
            else:
                return request.notifyFinish()
        else:
            raise ValueError("Unexpected return value: %r" % (result,))

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_calls_callback(self):
        got_callback = defer.Deferred()
        request = DummyPostRequest([''], content='{}')
        resource = CallbackResource(got_callback.callback, self.reactor)
        d = self._render(resource, request)
        def rendered(ignored):
            self.assertEquals('<html></html>', "".join(request.written))
        d.addCallback(rendered)
        return defer.gatherResults([d, got_callback])

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_returns_method_and_body(self):
        got_callback = defer.Deferred()
        def on_post((method, body)):
            self.assertEqual("POST", method)
            self.assertEqual(["a"], json.loads(body))
        got_callback.addCallback(on_post)
        request = DummyPostRequest([''], content='["a"]')
        resource = CallbackResource(got_callback.callback, self.reactor)
        d = self._render(resource, request)
        return defer.gatherResults([d, got_callback])


class WebServerTests(TestCase):

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_errback(self):
        # WebServer.run sets up a webserver with an errback URL.  When that
        # URL is posted to, an internal deferred will errback with the body of
        # the request.
        payload = {'traceback': 'foo', 'type': 'bar'}
        ws = WebServer()
        d = ws.run()
        def check_web_server((root, url, metadata)):
            errback_url = metadata['errback_url']
            agent = Agent(self.reactor)
            error_body = StringIO(json.dumps(payload))
            return agent.request(
                'PUT', errback_url, bodyProducer=FileBodyProducer(error_body))
        d.addCallback(check_web_server)

        def check_errback_response(response):
            self.assertEqual(200, response.code)
        d.addCallback(check_errback_response)

        def got_success(result):
            self.fail("Excepted errback, got success instead: %r" % (result,))
        def got_failure(failure):
            (method, body) = failure.value
            self.assertEqual(('PUT', payload), (method, json.loads(body)))
        ws._on_callback.addCallbacks(got_success, got_failure)

        d = defer.gatherResults([ws._on_callback, d])
        return d.addBoth(ws.shut_down_web_server)

    @run_test_with(AsynchronousDeferredRunTest.make_factory(timeout=10))
    def test_callback(self):
        payload = {}
        ws = WebServer()
        d = ws.run()
        def check_web_server((root, url, metadata)):
            callback_url = metadata['callback_url']
            agent = Agent(self.reactor)
            callback_body = StringIO(json.dumps(payload))
            return agent.request(
                'PUT', callback_url,
                bodyProducer=FileBodyProducer(callback_body))
        d.addCallback(check_web_server)

        def check_response(response):
            self.assertEqual(200, response.code)
        d.addCallback(check_response)

        def got_success((method, body)):
            self.assertEqual(('PUT', payload), (method, json.loads(body)))
        ws._on_callback.addCallback(got_success)

        d = defer.gatherResults([ws._on_callback, d])
        return d.addBoth(ws.shut_down_web_server)


class TestPkgmeServiceError(TestCase):

    def test_non_json_body(self):
        e = PkgmeServiceError('whatever')
        self.assertEqual('whatever', e.body)
        self.assertEqual('Non-JSON response', e.traceback)

    def test_json_body(self):
        data = {'foo': 'bar'}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual(data, e.body)
        self.assertEqual('No traceback', e.traceback)
        self.assertIs(None, e.error)

    def test_error_in_json_body(self):
        data = {'error': 'foo'}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual({}, e.body)
        self.assertEqual('foo', e.traceback)
        self.assertIs(None, e.error)

    def test_traceback_in_error(self):
        data = {'error': {'traceback': 'foo', 'type': 'Foo'}}
        body = json.dumps(data)
        e = PkgmeServiceError(body)
        self.assertEqual({}, e.body)
        self.assertEqual('foo', e.traceback)
        self.assertEqual({'type': 'Foo'}, e.error)


class TestWrapPkgmeServiceError(TestCase):

    def test_passthrough_non_tuple(self):
        f = Failure(TimeoutError())
        self.assertIs(f, wrap_pkgme_service_error(f))

    def test_put_in_pkgme_service_error(self):
        data = {'error': {'traceback': 'foo', 'type': 'Foo'}}
        body = json.dumps(data)
        expected = PkgmeServiceError(body)
        failure = wrap_pkgme_service_error(Failure(('PUT', body)))
        self.assertEqual(
            (expected.body, expected.traceback, expected.error),
            (failure.value.body, failure.value.traceback,
             failure.value.error))
