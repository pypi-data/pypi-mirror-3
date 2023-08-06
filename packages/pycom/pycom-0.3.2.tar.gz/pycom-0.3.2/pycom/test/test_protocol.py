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

"""Tests for pycom.protocol."""

import json

import six
import zmq

import pycom
from pycom import constants, exceptions, protocol

from .utils import unittest, Replacer


class TestRequestToWire(unittest.TestCase):

    def testOk(self):
        result = protocol.request_to_wire("iface.name", "method", {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "session_id": None,
            "args": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWithSession(self):
        result = protocol.request_to_wire("iface.name", "method", {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        }, 42)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "session_id": 42,
            "args": {
                "number": 1.0,
                "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
                "array": ["string", 123, 45.6, {"1": 2}]
            }
        })

    def testWrongArgs(self):
        self.assertRaises(TypeError,
            protocol.request_to_wire, "iface.name", "method", object())


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
        result = protocol.request_from_wire(result)
        self.assertIsInstance(result, pycom.Request)
        self.assertEqual(result.interface, "iface.name")
        self.assertEqual(result.method, "method")
        self.assertDictEqual(result.args, {
            "number": 1.0,
            "string": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "array": ["string", 123, 45.6, {"1": 2}]
        })

    def testWithSession(self):
        sessid = protocol._session_factory.new().session_id
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
        result = protocol.request_from_wire(result)
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
            protocol.request_from_wire, result)


class TestResponseToWire(unittest.TestCase):

    def testWithError(self):
        result = protocol.response_to_wire(100500,
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"), {"2": 3}, 42)
        self.assertIsInstance(result, six.binary_type)
        self.assertDictEqual(json.loads(result.decode("utf-8")), {
            "code": 100500,
            "error": six.u("\u041f\u0440\u0438\u0432\u0435\u0442"),
            "session_id": 42
        })

    def testWoError(self):
        result = protocol.response_to_wire(0,
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"), {"2": 3}, 42)
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
        result, session_id = protocol.response_from_wire(result)
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
        result, session_id = protocol.response_from_wire(result)
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
            protocol.response_from_wire, result)

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
            protocol.response_from_wire, result)


class FakeClientSocket(object):

    poll_success = 3
    recv_success = True
    timeout = constants.PROTO_DEFAULT_TIMEOUT
    send_errno = 0
    recv_errno = 0

    def poll(self, timeout=None, flags=0):
        assert timeout == self.timeout
        assert flags in (0, zmq.POLLOUT)
        self.poll_success -= 1
        return self.poll_success

    def send_multipart(self, data, flags=0):
        assert flags == zmq.NOBLOCK
        assert len(data) == 2
        assert data[0] == constants.PROTO_CMD_CALL
        if self.send_errno:
            raise zmq.ZMQError(self.send_errno)
        self.data = data[1]

    def recv_multipart(self, flags=0):
        assert flags == zmq.NOBLOCK
        if self.recv_errno:
            raise zmq.ZMQError(self.recv_errno)
        status = constants.PROTO_STATUS_SUCCESS if self.recv_success \
            else constants.PROTO_STATUS_FAILURE
        return [status, six.b("""{
            "code": 0,
            "result": %s
        }""" % self.data.decode("utf-8"))]


class FakeClientSocketError(FakeClientSocket):

    def recv_multipart(self, flags=0):
        return [constants.PROTO_STATUS_SUCCESS, six.b("""{
            "code": %d,
            "result": {}
        }""" % constants.ERROR_METHOD_NOT_FOUND)]


class RemoteComponentTest(unittest.TestCase):
    # This case is mostly using fake socket

    def testSuccess(self):
        sock = FakeClientSocket()
        comp = pycom.RemoteComponent(sock, "iface.name")
        result = comp.invoke("method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))
        self.assertDictEqual(result, {
            "interface": "iface.name",
            "method": "method",
            "version": "1.0",
            "session_id": None,
            "args": six.u("\u041f\u0440\u0438\u0432\u0435\u0442")
        })

    def testPollFailure1(self):
        sock = FakeClientSocket()
        sock.poll_success = 1
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testPollFailure2(self):
        sock = FakeClientSocket()
        sock.poll_success = 2
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testFailingService(self):
        sock = FakeClientSocket()
        sock.recv_success = False
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testSendUnavailable(self):
        sock = FakeClientSocket()
        sock.send_errno = zmq.EAGAIN
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testRecvUnavailable(self):
        sock = FakeClientSocket()
        sock.recv_errno = zmq.EAGAIN
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testSendFailure(self):
        sock = FakeClientSocket()
        sock.send_errno = 100500
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(zmq.ZMQError,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testRecvFailure(self):
        sock = FakeClientSocket()
        sock.recv_errno = 100500
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(zmq.ZMQError,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testMethodNotFound(self):
        sock = FakeClientSocketError()
        comp = pycom.RemoteComponent(sock, "iface.name")
        self.assertRaises(exceptions.MethodNotFound,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))


# Private

def _encode(s):
    return six.binary_type(six.u(s).encode("utf-8"))
