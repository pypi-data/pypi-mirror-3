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

"""Tests for zerojson.client."""

import json

import six
import zmq

import zerojson
from .. import constants, exceptions

from ..testing import unittest


class ClosedSuccessfully(Exception): pass


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

    def send_multipart(self, data, flags=0, **kw):
        assert flags == zmq.NOBLOCK
        assert len(data) == 2
        assert data[0] == constants.PROTO_CMD_CALL
        if self.send_errno:
            raise zmq.ZMQError(self.send_errno)
        self.data = data[1]

    def recv_multipart(self, flags=0, **kw):
        assert flags == zmq.NOBLOCK
        if self.recv_errno:
            raise zmq.ZMQError(self.recv_errno)
        status = constants.PROTO_STATUS_SUCCESS if self.recv_success \
            else constants.PROTO_STATUS_FAILURE
        return [status, six.b("""{
            "code": 0,
            "result": %s
        }""" % self.data.decode("utf-8"))]

    def close(self, **kwargs):
        raise ClosedSuccessfully(repr(kwargs))


class FakeClientSocketSession(FakeClientSocket):

    def recv_multipart(self, flags=0, **kw):
        return [constants.PROTO_STATUS_SUCCESS, six.b("""{
            "code": 0,
            "result": {},
            "session_id": "banana!"
        }""")]


class FakeClientSocketAttachment(FakeClientSocket):

    def send_multipart(self, data, flags=0, **kw):
        assert flags == zmq.NOBLOCK
        assert len(data) == 3
        assert data[0] == constants.PROTO_CMD_CALL
        assert data[2] == "attachment!"
        self.data = data[1]

    def recv_multipart(self, flags=0, **kw):
        return [constants.PROTO_STATUS_SUCCESS, self.data]


class FakeClientSocketAttachment2(FakeClientSocket):

    def send_multipart(self, data, flags=0, **kw):
        assert flags == zmq.NOBLOCK
        assert len(data) == 2
        assert data[0] == constants.PROTO_CMD_CALL
        self.data = data[1]

    def recv_multipart(self, flags=0, **kw):
        return [constants.PROTO_STATUS_SUCCESS, self.data, b"attachment!"]


class FakeClientSocketError(FakeClientSocket):

    def __init__(self, error):
        self.error = error

    def recv_multipart(self, flags=0, **kw):
        return [constants.PROTO_STATUS_SUCCESS, six.b("""{
            "code": %d,
            "result": {}
        }""" % self.error)]


class RemoteComponentTest(unittest.TestCase):
    # This case is mostly using fake socket

    def testInvalidAddress(self):
        self.assertRaisesRegexp(ValueError, "Invalid address",
            zerojson.Client, "banana!", "iface.name")

    def testUnavailable(self):
        self.assertRaises(exceptions.ServiceNotAvailable,
            zerojson.Client, "inproc:///banana!", "iface.name")

    def testSuccess(self):
        sock = FakeClientSocket()
        comp = zerojson.Client(sock, "iface.name")
        result = comp.invoke("method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))
        self.assertDictEqual(result, {
            "interface": "iface.name",
            "method": "method",
            "version": constants.PROTO_VERSION,
            "args": six.u("\u041f\u0440\u0438\u0432\u0435\u0442")
        })
        self.assertEqual(comp.session_id, None)

    def testSuccessWithSession(self):
        sock = FakeClientSocketSession()
        comp = zerojson.Client(sock, "iface.name")
        result = comp.invoke("method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))
        self.assertEqual(result, {})
        self.assertEqual(comp.session_id, "banana!")

    def testSuccessWithAttachment(self):
        sock = FakeClientSocketAttachment()
        comp = zerojson.Client(sock, "iface.name")
        status, message = comp._send_message(constants.PROTO_CMD_CALL,
            "42", constants.PROTO_DEFAULT_TIMEOUT, attachment="attachment!")
        self.assertEqual(status, constants.PROTO_STATUS_SUCCESS)
        self.assertEqual(message, "42")

    def testSuccessWithAttachment2(self):
        sock = FakeClientSocketAttachment2()
        comp = zerojson.Client(sock, "iface.name")
        status, message, att = comp._send_message(constants.PROTO_CMD_CALL,
            "42", constants.PROTO_DEFAULT_TIMEOUT)
        self.assertEqual(status, constants.PROTO_STATUS_SUCCESS)
        self.assertEqual(message, "42")
        self.assertEqual(att, b"attachment!")

    def testClose(self):
        sock = FakeClientSocket()
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaisesRegexp(ClosedSuccessfully, "{}",
            comp.close)
        self.assertRaisesRegexp(ClosedSuccessfully, "{'linger': 0}",
            comp.close, linger=0)

    def testPollFailure1(self):
        sock = FakeClientSocket()
        sock.poll_success = 1
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testPollFailure2(self):
        sock = FakeClientSocket()
        sock.poll_success = 2
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testFailingService(self):
        sock = FakeClientSocket()
        sock.recv_success = False
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testSendUnavailable(self):
        sock = FakeClientSocket()
        sock.send_errno = zmq.EAGAIN
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testRecvUnavailable(self):
        sock = FakeClientSocket()
        sock.recv_errno = zmq.EAGAIN
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.ServiceNotAvailable,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testSendFailure(self):
        sock = FakeClientSocket()
        sock.send_errno = 100500
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(zmq.ZMQError,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testRecvFailure(self):
        sock = FakeClientSocket()
        sock.recv_errno = 100500
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(zmq.ZMQError,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testMethodNotFound(self):
        sock = FakeClientSocketError(constants.ERROR_METHOD_NOT_FOUND)
        comp = zerojson.Client(sock, "iface.name")
        self.assertRaises(exceptions.MethodNotFound,
            comp.invoke, "method",
            six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))

    def testRemoteError(self):
        sock = FakeClientSocketError(constants.ERROR_BAD_REQUEST)
        comp = zerojson.Client(sock, "iface.name")
        with self.assertRaises(exceptions.RemoteError) as ctx:
            comp.invoke("method",
                six.u("\u041f\u0440\u0438\u0432\u0435\u0442"))
        self.assertEqual(ctx.exception.code, constants.ERROR_BAD_REQUEST)
