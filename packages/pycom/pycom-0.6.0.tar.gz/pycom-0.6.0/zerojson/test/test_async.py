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

"""Tests for zerojson.async."""

import functools
import threading

import zmq.eventloop.ioloop

import zerojson
from .. import common, constants, exceptions

from ..testing import unittest
from .test_server import BaseIntegrationTest


class TestFuture(BaseIntegrationTest, unittest.TestCase):

    def testFutureCall(self):
        def _finish(future):
            future.response(42)
            self.assertRaises(RuntimeError, future.response, 42)

        def _handler(request):
            self.assertEqual(request.interface, "test.testFutureCall")
            future = zerojson.Future(request)
            self.ioloop.add_callback(functools.partial(_finish, future))
            return future

        def _check():
            cli = zerojson.Client(self.address, "test.testFutureCall")
            self.assertEqual(cli.invoke("method", args=100500), 42)

        self._runMe(_handler, _check)

    def testFutureAttachments(self):
        def _finish(future):
            future.response(42, attachment=b"Hello")

        def _handler(request):
            self.assertEqual(request.interface, "test.testFutureAttachments")
            future = zerojson.Future(request)
            self.ioloop.add_callback(functools.partial(_finish, future))
            return future

        def _check():
            cli = zerojson.Client(self.address, "test.testFutureAttachments")
            self.assertEqual(cli.invoke("method", args=100500), (42, b"Hello"))

        self._runMe(_handler, _check)

    def testFutureIsNow(self):
        def _handler(request):
            self.assertEqual(request.interface, "test.testFutureCall")
            future = zerojson.Future(request)
            future.response(42)
            self.assertRaises(RuntimeError, future.response, 42)
            self.assertRaises(RuntimeError, future.error, 42)
            return future

        def _check():
            cli = zerojson.Client(self.address, "test.testFutureCall")
            self.assertEqual(cli.invoke("method", args=100500), 42)

        self._runMe(_handler, _check)

    def testFutureError(self):
        def _finish(future):
            future.error(constants.ERROR_BAD_REQUEST, "testFutureError")
            self.assertRaises(RuntimeError, future.response, 42)
            self.assertRaises(RuntimeError, future.error, 42)

        def _handler(request):
            self.assertEqual(request.interface, "test.testFutureError")
            future = zerojson.Future(request)
            self.ioloop.add_callback(functools.partial(_finish, future))
            return future

        def _check():
            cli = zerojson.Client(self.address, "test.testFutureError")
            with self.assertRaisesRegexp(zerojson.RemoteError,
                    "testFutureError") as ctx:
                cli.invoke("method", args=100500)
            self.assertEqual(ctx.exception.code,
                zerojson.constants.ERROR_BAD_REQUEST)

        self._runMe(_handler, _check)

    def testFutureException(self):
        def _finish(future):
            try:
                assert 0
            except:
                future.exception()
                self.assertRaises(RuntimeError, future.response, 42)
                self.assertRaises(RuntimeError, future.error, 42)

        def _handler(request):
            self.assertEqual(request.interface, "test.testFutureException")
            future = zerojson.Future(request)
            self.ioloop.add_callback(functools.partial(_finish, future))
            return future

        def _check():
            cli = zerojson.Client(self.address, "test.testFutureException")
            with self.assertRaisesRegexp(zerojson.RemoteError,
                    "Unknown error during request") as ctx:
                cli.invoke("method", args=100500)
            self.assertEqual(ctx.exception.code,
                zerojson.constants.ERROR_UNKNOWN)

        self._runMe(_handler, _check)
