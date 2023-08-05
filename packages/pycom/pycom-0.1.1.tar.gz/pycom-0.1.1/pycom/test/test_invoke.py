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

"""Tests for pycom.invoke."""

import zmq

import pycom
from pycom import constants, exceptions, invoke, protocol
from pycom.test.utils import unittest, Replacer
from pycom.test.test_interfaces import BaseTest

class DirectInvokerTest(BaseTest, unittest.TestCase):

    def testErrorOnWrongWrapped(self):
        self.assertRaises(TypeError, invoke.DirectInvoker, object())

    def testCallExisting(self):
        iface = "test.test_invoke.DirectInvokerTest.testCall"
        meth1 = "method1"
        testObject1 = object()
        testObject2 = object()

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request):
                assert self.__interface__.name == iface
                assert request.args is testObject1
                return testObject2

        invoker = invoke.DirectInvoker(InterfaceWithMethods)
        self.assertIs(invoker.invoke(meth1, args=testObject1), testObject2)

    def testCallNonExisting(self):
        iface = "test.test_invoke.DirectInvokerTest.testCallNonExisting"
        meth1 = "method1"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request): pass  # pragma: no cover

        invoker = invoke.DirectInvoker(InterfaceWithMethods)
        self.assertRaises(exceptions.MethodNotFound, invoker.invoke, "banana!")

    def testCallWrongName(self):
        iface = "test.test_invoke.DirectInvokerTest.testCallWrongName"
        meth1 = "method1"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request): pass  # pragma: no cover

        invoker = invoke.DirectInvoker(InterfaceWithMethods)
        self.assertRaises(exceptions.MethodNotFound, invoker.invoke, "m1")


def fake_send_request(socket, iface, method, args, timeout=None):
    assert type(socket) is object
    assert iface == "test.iface"
    assert method == "method"
    assert args == "dummy_args"
    assert timeout == 3
    return "result"


class RemoteInvokerTest(unittest.TestCase):

    def testCallProtocol(self):
        with Replacer(protocol, "send_request", fake_send_request):
            invoker = invoke.RemoteInvoker(object(), "test.iface")
            result = invoker.invoke("method", args="dummy_args", timeout=3)
            self.assertEqual(result, "result")
