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

"""Tests for pycom.zerojson.call."""

import json

import six
import zmq

import pycom
from pycom import constants, exceptions
from pycom.zerojson import call

from .utils import unittest


class TestRequestToWire(unittest.TestCase):

    def testOk(self):
        result = call.CallCommand().request_to_wire("iface.name", "method", {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": constants.PROTO_VERSION,
            "session_id": None,
            "args": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWithSession(self):
        result = call.CallCommand().request_to_wire("iface.name", "method", {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        }, 42)
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

    def testWrongArgs(self):
        self.assertRaises(TypeError,
            call.CallCommand().request_to_wire, "iface.name", "method", object())


class TestRequestFromWire(unittest.TestCase):

    def testOk(self):
        result = _encode("""{
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
        self.assertIsInstance(result, pycom.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertDictEqual(result.args, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testWithSession(self):
        command = call.CallCommand()
        sessid = command.session_factory.new().session_id
        result = _encode("""{
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "session_id": "%s",
            "args": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""" % sessid)
        result = command.request_from_wire(result)
        self.assertIsInstance(result, pycom.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertEqual(result.session.session_id, sessid)
        self.assertDictEqual(result.args, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testBadRequest(self):
        result = _encode("""{
            "interface": "iface.name",
            "version": "1.0",
            "args": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaises(exceptions.BadRequest,
            call.CallCommand().request_from_wire, result)


class TestResponseToWire(unittest.TestCase):

    def testWithError(self):
        result = call.CallCommand().response_to_wire(100500,
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"), {"2": 3}, 42)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 100500,
            "error": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "session_id": 42
        })

    def testWoError(self):
        result = call.CallCommand().response_to_wire(0, None, {"2": 3}, 42)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 0,
            "result": {"2": 3},
            "session_id": 42
        })


class TestResponseFromWire(unittest.TestCase):

    def testOk(self):
        result = _encode("""{
            "code": 0,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        result, session_id = call.CallCommand().response_from_wire(result)
        self.assertDictEqual(result, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertEqual(session_id, None)

    def testWithSession(self):
        result = _encode("""{
            "code": 0,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            },
            "session_id": 42
        }""")
        result, session_id = call.CallCommand().response_from_wire(result)
        self.assertDictEqual(result, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertEqual(session_id, 42)

    def testErrorWithString(self):
        result = _encode("""{
            "code": 100500,
            "error": "ERROR",
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaisesRegexp(pycom.RemoteError, "ERROR",
            call.CallCommand().response_from_wire, result)

    def testErrorWoString(self):
        result = _encode("""{
            "code": 100500,
            "result": {
                "number": 1.0,
                "string": "\u041f\u0440\u0438\u0432\u0435\u0442",
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        }""")
        self.assertRaisesRegexp(pycom.RemoteError, "Remote error #100500",
            call.CallCommand().response_from_wire, result)


# Private

def _encode(s):
    return six.binary_type(six.u(s).encode("utf-8"))
