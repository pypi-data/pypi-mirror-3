#   PyCOM - Distributed Component Model for Python
#   Copyright (c) 2011-2012, Dmitry "Divius" Tantsur
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following disclaimer
#     in the documentation and/or other materials provided with the
#     distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests for zerojson.server."""

import collections
import threading

import zmq.eventloop.ioloop

import zerojson
from .. import common, constants, exceptions

from ..testing import unittest, AddressGenerationMixin


class TestProcessing(unittest.TestCase):

    def testMessageHandler(self):
        server = zerojson.Server([])

        def _command(command_name, json_body, *other_parts):
            self.assertEqual(command_name, b"FOO!")
            self.assertEqual(json_body, b"BODY")
            self.assertEqual(other_parts, ())
            return [b"OK!", b"42"]

        class FakeServerSocket(object):

            def send_multipart(self, data, flags=0, **kw):
                assert data == [b"", b"OK!", b"42"], data

        server._command = _command
        sock = FakeServerSocket()

        fake_msg = collections.namedtuple("FakeMessage", "bytes")
        server._message_handler(sock,
            [fake_msg(b""), fake_msg(b"FOO!"), fake_msg(b"BODY")])


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.server = zerojson.Server([])

        self.non_existing_command = "banana!"

        class FakeBaseCommand(object):

            def response_to_wire(self2, response):
                self.assertEqual(response.code,
                    zerojson.constants.ERROR_BAD_REQUEST)
                self.assertEqual(response.message,
                    "Unknown command: %s" % self.non_existing_command)
                self.assertEqual(response.result, None)
                return "ERROR"

        class FakeCommand(object):

            def process_request(self, json_body, x, y):
                return [json_body, x, y]

        self.existing_command = "demo!"

        self.server._base = FakeBaseCommand()
        self.server.commands = {
            self.existing_command: FakeCommand()
        }

    def testKnownCommand(self):
        self.assertEqual(self.server._command(self.existing_command,
            "BODY", "1", "2"),
            [zerojson.constants.PROTO_STATUS_SUCCESS, "BODY", "1", "2"])

    def testUnknownCommand(self):
        self.assertEqual(self.server._command(self.non_existing_command,
            "BODY", "1", "2"),
            [zerojson.constants.PROTO_STATUS_SUCCESS, "ERROR"])


# Here we use some knowledge of ZMQ internals to check added handlers.
# Shame on us!

class TestSetup(AddressGenerationMixin, unittest.TestCase):

    def testSetup(self):
        addresses = [self.genAddress(), self.genAddress()]
        server = zerojson.Server(addresses)
        loop = zmq.eventloop.ioloop.IOLoop()
        loop._handlers.clear()
        server.setup(ioloop=loop)
        self.assertEqual(len(loop._handlers), 2)
        assert all(isinstance(x, zmq.Socket) for x in loop._handlers)

# Following tests are mostly integration ones!
# Not only do we test basic server behaviour and some corner cases,
# but also we test how well Server and Client play with each other.
# The only things that is completely "dummy" is call handling.

class BaseIntegrationTest(AddressGenerationMixin):

    timeout = 3

    def setUp(self):
        super(BaseIntegrationTest, self).setUp()

        self.address = self.genAddress()
        self.ioloop = zmq.eventloop.ioloop.IOLoop()

    def _genServer(self, handler):
        server = zerojson.Server([self.address])
        server.handle_call = handler
        server.setup(ioloop=self.ioloop)
        return server

    def _runMe(self, handler, check):
        ok = {"value": False}  # Need a mutable object

        def _real_check():
            try:
                check()
                ok["value"] = True
            finally:
                self.ioloop.add_callback(self.ioloop.stop)

        self._genServer(handler)
        thread = threading.Thread(target=_real_check)
        thread.start()
        self.ioloop.start()
        self.assertTrue(ok["value"])


class TestClientServer(BaseIntegrationTest, unittest.TestCase):

    def testSimpleCall(self):
        def _handler(request):
            self.assertEqual(request.interface, "test.testSimpleCall")
            self.assertEqual(request.method, "method")
            self.assertEqual(request.args, 100500)
            return request.response(42)

        def _check():
            cli = zerojson.Client(self.address, "test.testSimpleCall")
            self.assertEqual(cli.invoke("method", args=100500), 42)

        self._runMe(_handler, _check)

    def testAttachmentIn(self):
        def _handler(request):
            return request.response(request.attachment.decode("utf-8"))

        def _check():
            cli = zerojson.Client(self.address, "test.testAttachmentIn")
            self.assertEqual(cli.invoke("method", attachment=b"Hello"),
                "Hello")

        self._runMe(_handler, _check)

    def testAttachmentOut(self):
        def _handler(request):
            return request.response(42, attachment=b"Bye")

        def _check():
            cli = zerojson.Client(self.address, "test.testAttachmentIn")
            self.assertEqual(cli.invoke("method"), (42, b"Bye"))

        self._runMe(_handler, _check)

    def testSimpleFailure(self):
        def _handler(request):
            raise zerojson.BadRequest("testSimpleFailure")

        def _check():
            cli = zerojson.Client(self.address, "test.testSimpleFailure")
            with self.assertRaisesRegexp(zerojson.RemoteError,
                    "testSimpleFailure") as ctx:
                cli.invoke("method", args=100500)
            self.assertEqual(ctx.exception.code,
                zerojson.constants.ERROR_BAD_REQUEST)

        self._runMe(_handler, _check)

    def testSimpleFailure2(self):
        def _handler(request):
            return request.error(zerojson.constants.ERROR_BAD_REQUEST,
                "testSimpleFailure2")

        def _check():
            cli = zerojson.Client(self.address, "test.testSimpleFailure2")
            with self.assertRaisesRegexp(zerojson.RemoteError,
                    "testSimpleFailure2") as ctx:
                cli.invoke("method", args=100500)
            self.assertEqual(ctx.exception.code,
                zerojson.constants.ERROR_BAD_REQUEST)

        self._runMe(_handler, _check)

    def testSession(self):
        def _handler(request):
            if request.args:
                request.session["test"] = request.args

            return request.response(request.session["test"])

        def _check():
            cli = zerojson.Client(self.address, "test.testSession")
            self.assertEqual(cli.invoke("method", args=42), 42)
            self.assertEqual(cli.invoke("method", args=None), 42)
            self.assertEqual(cli.invoke("method", args=100500), 100500)

        self._runMe(_handler, _check)

    def testSpoiledSession(self):
        def _handler(request):
            request.session.session_id = "banana!"
            return request.response(42)

        def _check():
            cli = zerojson.Client(self.address, "test.testSession")
            self.assertEqual(cli.invoke("method"), 42)
            with self.assertRaisesRegexp(zerojson.RemoteError,
                    "Session 'banana!' has expired") as ctx:
                cli.invoke("method")
            self.assertEqual(ctx.exception.code,
                zerojson.constants.ERROR_SESSION_EXPIRED)

        self._runMe(_handler, _check)

    def testDiscardedSession(self):
        def _handler(request):
            if request.args:
                request.session["test"] = request.args
            elif request.args is None:
                request.session.discard()

            return request.response(request.session.get("test", None))

        def _check():
            cli = zerojson.Client(self.address, "test.testDiscardedSession")
            self.assertEqual(cli.invoke("method", args=42), 42)
            self.assertEqual(cli.invoke("method", args=0), 42)
            self.assertEqual(cli.invoke("method", args=None), None)

        self._runMe(_handler, _check)
