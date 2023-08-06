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

"""Tests for pycom.ext.checks."""

import pycom
import zerojson
from pycom import base, constants, nsclient

from .test_interfaces import BaseTest
from zerojson.testing import unittest, replacer


class DummyNS(object):

    def __init__(self, owner):
        self.owner = owner

    def invoke(self, method_name, args=None):
        self.owner.assertIn(method_name,
            [constants.NS_METHOD_LOCATE, constants.GENERIC_METHOD_INTROSPECT])
        if method_name == constants.NS_METHOD_LOCATE:
            self.owner.assertEqual(args["interface"], "dummy.iface")
            return {"address": "proxy://dummy"}
        else:
            return {"methods": []}

def dummy_component(owner):
    def _wrapped(address, iface, *args, **kwargs):
        assert address == "proxy://dummy", address
        assert iface == "dummy.iface", iface
        return DummyNS(owner)
    return _wrapped


class TestContext(BaseTest, unittest.TestCase):

    def setUp(self):
        super(TestContext, self).setUp()
        self.context = pycom.ProxyContext()
        self.oldNS = nsclient._pop_cached_ns(ctx=self.context._wrapped)
        nsclient._restore_cached_ns(DummyNS(self), ctx=self.context._wrapped)

    def tearDown(self):
        self.context = None
        super(TestContext, self).tearDown()

    def testNameserver(self):
        result = self.context.nameserver()
        self.assertIsInstance(result, pycom.ProxyComponent)
        self.assertIsInstance(result._wrapped, DummyNS)

    def testLocate(self):
        with replacer(nsclient, "RemoteComponent", dummy_component(self)):
            result = self.context.locate("dummy.iface")
            self.assertIsInstance(result, pycom.ProxyComponent)

    def testConnect(self):
        with replacer(nsclient, "RemoteComponent", dummy_component(self)):
            result = self.context.connect("proxy://dummy", "dummy.iface")
            self.assertIsInstance(result, pycom.ProxyComponent)


class TestContextWrap(TestContext):

    def setUp(self):
        super(TestContext, self).setUp()
        orig_context = pycom.Context()
        self.oldNS = nsclient._pop_cached_ns(ctx=orig_context)
        nsclient._restore_cached_ns(DummyNS(self), ctx=orig_context)

        self.context = pycom.ProxyContext(orig_context)


class TestComponent(BaseTest, unittest.TestCase):

    def testCorrectWrapping(self):
        iface = "test.test_proxy.TestComponent.testCorrectWrapping"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method
            def meth1(self, request):
                """DOC."""
                pass  # pragma: no cover

            @pycom.method
            def meth2(self, request): pass  # pragma: no cover

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.meth1.__name__, "meth1")
            self.assertEqual(component.meth1.__doc__, "DOC.")
            self.assertEqual(component.meth2.__doc__,
                "Remote method '%s.meth2'." % iface)

    def testRequiredOnly(self):
        iface = "test.test_proxy.TestComponent.testRequiredOnly"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method(meth)
            def meth1(self, request, arg1, arg2):
                return [arg1, arg2]

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.method1(1, 2), [1, 2])
            self.assertEqual(component.method1(arg1=1, arg2=2), [1, 2])
            self.assertEqual(component.method1(1, arg2=2), [1, 2])

            self.assertRaisesRegexp(TypeError, "multiple values",
                component.method1, 1, arg1=0, arg2=2)
            self.assertRaisesRegexp(TypeError, "required",
                component.method1, 1)
            self.assertRaisesRegexp(TypeError, "required",
                component.method1)
            self.assertRaisesRegexp(TypeError, "required",
                component.method1, arg2=2)
            self.assertRaises(AttributeError, lambda: component.xxx())
            self.assertRaises(AttributeError, lambda: component.meth1())
            self.assertRaisesRegexp(TypeError, "Too many positional arguments",
                component.method1, 1, 2, 3)

            component.introspect()

    def testOptionalOnly(self):
        iface = "test.test_proxy.TestComponent.testOptionalOnly"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method(meth)
            def meth1(self, request, arg1=0, arg2=0):
                return [arg1, arg2]

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.method1(arg1=1, arg2=2), [1, 2])
            self.assertEqual(component.method1(), [0, 0])

            self.assertRaisesRegexp(TypeError, "Too many positional arguments",
                component.method1, 1)

    def testWithSingleResult(self):
        iface = "test.test_proxy.TestComponent.testWithSingleResult"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method(meth, results=("x",))
            def meth1(self, request, arg1, arg2):
                return arg1 + arg2

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.method1(1, 2), 3)

    def testWithMultipleResults(self):
        iface = "test.test_proxy.TestComponent.testWithMultipleResults"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method(meth, results=("x", "y"))
            def meth1(self, request, arg1, arg2):
                return arg1 + arg2, arg1 - arg2

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.method1(1, 2), (3, -1))
            self.assertEqual(component.method1(1, 2).x, 3)
            self.assertEqual(component.method1(1, 2).y, -1)


class TestComponentAttachments(BaseTest, unittest.TestCase):

    def testSimple(self):
        iface = "test.test_proxy.TestComponentAttachments.testAttachments"

        @pycom.interface(iface)
        class SimpleInterface(pycom.Service):

            @pycom.method(results=("out",), attachments=("inc", "out"))
            def method1(self, request, inc):
                return inc

        with pycom.ProxyComponent(SimpleInterface.__interface__) as component:
            self.assertEqual(component.method1(inc=b"Test"), b"Test")


class ContextHooksTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(ContextHooksTest, self).setUp()

        @pycom.interface(constants.NS_INTERFACE)
        class DummyNameserver(pycom.Service):

            @pycom.method
            def demo(self2, request, value):
                return value

    def testPrehook(self):
        def _hook(comp, request):
            if request.method != "demo":
                return request
            self.assertIsInstance(comp, base.BaseComponent)
            self.assertIsInstance(request, zerojson.Request)
            request.args["value"] = -request.args["value"]
            return request

        ctx = pycom.ProxyContext()
        ctx.prehooks.append(_hook)
        self.assertEqual(ctx.nameserver().demo(42), -42)

    def testPosthook(self):
        def _hook(comp, response):
            if response.request.method != "demo":
                return response
            self.assertIsInstance(comp, base.BaseComponent)
            self.assertIsInstance(response, zerojson.Response)
            response.result = -response.result
            return response

        ctx = pycom.ProxyContext()
        ctx.posthooks.append(_hook)
        self.assertEqual(ctx.nameserver().demo(42), -42)
