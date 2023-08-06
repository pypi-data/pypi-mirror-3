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

"""Tests for zerojson.call."""

import json

import six
import zmq

import zerojson
from .. import call, constants, exceptions

from ..testing import encode_utf8, unittest


class TestRequestToWire(unittest.TestCase):

    def testOk(self):
        request = zerojson.Request("iface.name", "method", args={
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        result = call.CallCommand().request_to_wire(request)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": constants.PROTO_VERSION,
            "args": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWithSession(self):
        request = zerojson.Request("iface.name", "method", args={
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        result = call.CallCommand().request_to_wire(request, session_id=42)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": constants.PROTO_VERSION,
            "session_id": 42,
            "args": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWithExtensions(self):
        request = zerojson.Request("iface.name", "method", args={},
            extensions={
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        result = call.CallCommand().request_to_wire(request)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": constants.PROTO_VERSION,
            "args": {},
            "extensions": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWrongArgs(self):
        request = zerojson.Request("iface.name", "method", args=object())
        self.assertRaises(TypeError,
            call.CallCommand().request_to_wire, request)


class TestRequestFromWire(unittest.TestCase):

    def testOk(self):
        result = encode_utf8("""{
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "args": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        result = call.CallCommand().request_from_wire(result)
        self.assertIsInstance(result, zerojson.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertDictEqual(result.args, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testWithExtensions(self):
        result = encode_utf8("""{
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "args": {},
            "extensions": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        result = call.CallCommand().request_from_wire(result)
        self.assertIsInstance(result, zerojson.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertDictEqual(result.args, {})
        self.assertDictEqual(result.extensions, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testWithSession(self):
        command = call.CallCommand()
        result = encode_utf8("""{
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "session_id": "xyz",
            "args": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        result = command.request_from_wire(result)
        self.assertIsInstance(result, zerojson.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertEqual(result._session_id, "xyz")
        self.assertDictEqual(result.args, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testBadRequest(self):
        result = encode_utf8("""{
            "interface": "iface.name",
            "version": "1.0",
            "args": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaisesRegexp(zerojson.BadRequest, "Field .+ is required",
            call.CallCommand().request_from_wire, result)


class TestResponseToWire(unittest.TestCase):

    def testWithError(self):
        response = zerojson.Response(None, code=100500,
            message=six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            result={"2": 3}, session_id=42)
        result = call.CallCommand().response_to_wire(response)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 100500,
            "error": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "session_id": 42
        })

    def testWoError(self):
        response = zerojson.Response(None, result={"2": 3}, session_id=42)
        result = call.CallCommand().response_to_wire(response)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 0,
            "result": {"2": 3},
            "session_id": 42
        })

    def testWoSession(self):
        response = zerojson.Response(None, result={"2": 3}, session_id=None)
        result = call.CallCommand().response_to_wire(response)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 0,
            "result": {"2": 3}
        })

    def testWoErrorWExtensions(self):
        response = zerojson.Response(None, result={"2": 3}, session_id=42,
            extensions={"3": None})
        result = call.CallCommand().response_to_wire(response)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 0,
            "result": {"2": 3},
            "session_id": 42,
            "extensions": {"3": None}
        })


class TestResponseFromWire(unittest.TestCase):

    def testOk(self):
        result = encode_utf8("""{
            "code": 0,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        response = call.CallCommand().response_from_wire(result)
        self.assertIsInstance(response, zerojson.Response)
        self.assertDictEqual(response.result, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertEqual(response.session_id, None)

    def testWithExtensions(self):
        result = encode_utf8("""{
            "code": 0,
            "result": {},
            "extensions": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        response = call.CallCommand().response_from_wire(result)
        self.assertIsInstance(response, zerojson.Response)
        self.assertDictEqual(response.result, {})
        self.assertDictEqual(response.extensions, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertEqual(response.session_id, None)

    def testWithSession(self):
        result = encode_utf8("""{
            "code": 0,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            },
            "session_id": 42
        }""")
        response = call.CallCommand().response_from_wire(result)
        self.assertIsInstance(response, zerojson.Response)
        self.assertDictEqual(response.result, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertEqual(response.session_id, 42)

    def testErrorWithString(self):
        result = encode_utf8("""{
            "code": 100500,
            "error": "ERROR",
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaisesRegexp(zerojson.RemoteError, "ERROR",
            call.CallCommand().response_from_wire, result)

    def testErrorWoString(self):
        result = encode_utf8("""{
            "code": 100500,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaisesRegexp(zerojson.RemoteError, "Remote error #100500",
            call.CallCommand().response_from_wire, result)


fake_request = lambda: zerojson.Request("demo.iface", "meth", args=100500)


class TestRealProcessMessage(unittest.TestCase):

    def assertResponseOk(self, response):
        self.assertEqual(response.code, 0)
        self.assertFalse(response.message)

    def assertResponseFailed(self, response, code, msg=None):
        self.assertEqual(response.code, code)
        if msg is None:
            self.assertTrue(response.message)
        else:
            self.assertEqual(response.message, msg)
        self.assertFalse(response.result)

    def testOk(self):
        request = fake_request()

        def _check(checked_request):
            self.assertIs(checked_request, request)
            return checked_request.response(42)

        server = zerojson.Server([])
        server.handle_call = _check
        cmd = call.CallCommand(server)
        response = cmd.real_process_request(request)

        self.assertResponseOk(response)
        self.assertEqual(response.result, 42)

    def testTooManyAttachments(self):
        request = fake_request()

        server = zerojson.Server([])
        cmd = call.CallCommand(zerojson.Server([]))
        response = cmd.real_process_request(request, "abc", "def")

        self.assertResponseFailed(response,
            zerojson.constants.ERROR_BAD_REQUEST)

    def testIncomingAttachments(self):
        request = fake_request()

        def _check(checked_request):
            self.assertIs(checked_request, request)
            self.assertEqual(checked_request.attachment, b"Hello")
            return checked_request.response(42)

        server = zerojson.Server([])
        server.handle_call = _check
        cmd = call.CallCommand(server)
        response = cmd.real_process_request(request, b"Hello")

        self.assertResponseOk(response)
        self.assertEqual(response.result, 42)

    def testOutgoingAttachments(self):
        request = fake_request()

        def _check(checked_request):
            self.assertIs(checked_request, request)
            return checked_request.response(42, attachment=b"Bye")

        server = zerojson.Server([])
        server.handle_call = _check
        cmd = call.CallCommand(server)
        response = cmd.real_process_request(request)

        self.assertResponseOk(response)
        self.assertEqual(response.result, 42)
        self.assertEqual(response.attachment, b"Bye")

    def testKnownError(self):
        request = fake_request()

        def _check(checked_request):
            self.assertIs(checked_request, request)
            raise zerojson.RemoteError("testKnownError", code=100500)

        server = zerojson.Server([])
        server.handle_call = _check
        cmd = call.CallCommand(server)
        response = cmd.real_process_request(request)

        self.assertResponseFailed(response,
            100500, "testKnownError")

    def testUnknownError(self):
        request = fake_request()

        def _check(checked_request):
            self.assertIs(checked_request, request)
            raise RuntimeError()

        server = zerojson.Server([])
        server.handle_call = _check
        cmd = call.CallCommand(server)
        response = cmd.real_process_request(request)

        self.assertResponseFailed(response,
            zerojson.constants.ERROR_UNKNOWN)
