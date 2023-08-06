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

"""Tests for pycom.interfaces, pycom.helpers and pycom.base."""

import functools
import re

import pycom
import zerojson
from pycom import base, constants, interfaces, nsclient

from zerojson.testing import unittest, replacer

class BaseTest(object):

    def setUp(self):
        self.registry_bak = base.interface_registry.copy()
        base.interface_registry.clear()
        self.conf_bak = base.configuration.copy()
        base.configuration.clear()

    def tearDown(self):
        base.configuration.clear()
        base.configuration.update(self.conf_bak)
        base.interface_registry.clear()
        base.interface_registry.update(self.registry_bak)

class DecoratorsTest(BaseTest, unittest.TestCase):

    def testEmptyInterface(self):
        iface = "test.test_interfaces.DecoratorsTest.testEmptyInterface"

        @pycom.interface(iface)
        class EmptyInterface(object): pass

        self.assertIn(iface, base.interface_registry)
        self.assertIsInstance(EmptyInterface.__interface__, interfaces.Interface)
        self.assertIsInstance(EmptyInterface().__interface__, interfaces.Interface)
        self.assertEqual(EmptyInterface.__interface__.name, iface)

    def testInterfaceWithMethods(self):
        iface = "test.test_interfaces.DecoratorsTest.testInterfaceWithMethods"
        meth1 = "method1"
        meth2 = "method2"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self): pass # pragma: no cover

            @pycom.method(meth2)
            def m2(self): pass # pragma: no cover

        self.assertIn(meth1, InterfaceWithMethods.__interface__.methods)
        self.assertIn(meth2, InterfaceWithMethods.__interface__.methods)

    def testInterfaceWithImplicitMethods(self):
        iface = "test.test_interfaces.DecoratorsTest." \
            "testInterfaceWithImplicitMethods"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method
            def implicit_method(self): pass # pragma: no cover

        self.assertIn("implicit_method",
            InterfaceWithMethods.__interface__.methods)

    def testErrorOnDuplicateInterface(self):
        iface = "test.test_interfaces.DecoratorsTest.testErrorOnDuplicateInterface"

        @pycom.interface(iface)
        class EmptyInterface(object): pass

        def doIt():
            @pycom.interface(iface)
            class EmptyInterface2(object): pass

        self.assertRaisesRegexp(RuntimeError,
            "Interface %s is already registered" % re.escape(iface), doIt)

    def testErrorOnDuplicateMethod(self):
        iface = "test.test_interfaces.DecoratorsTest.testErrorOnDuplicateMethod"
        meth1 = "method1"

        def doIt():
            @pycom.interface(iface)
            class InterfaceWithMethods(object):

                @pycom.method(meth1)
                def m1(self): pass # pragma: no cover

                @pycom.method(meth1)
                def m2(self): pass # pragma: no cover

        self.assertRaisesRegexp(RuntimeError,
            "Function %s is already registered for interface %s" %
            (re.escape(meth1), re.escape(iface)), doIt)


FakeRequest = functools.partial(zerojson.Request, None, None)


class HooksTest(BaseTest, unittest.TestCase):

    def testPreHook(self):
        iface = "test.test_interfaces.HooksTest.testPreHook"
        meth1 = "method1"

        def _setup(meth):
            def _hook(iface, method, request):
                self.assertIsInstance(iface, interfaces.Interface)
                self.assertIsInstance(method, interfaces.Method)
                self.assertIsInstance(request, zerojson.Request)
                request.args = {"replaced": request.args}
                return request
            meth.__method__.prehooks.append(_hook)
            return meth

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @_setup
            @pycom.method(meth1)
            def m1(self2, request):
                self.assertDictEqual(request.args, {"replaced": 42})
                return 100500

        instance = InterfaceWithMethods()
        response = instance.m1.__method__.call(instance.__interface__,
            FakeRequest(args=42))
        self.assertEqual(response.result, 100500)

    def testPostHook(self):
        iface = "test.test_interfaces.HooksTest.testPostHook"
        meth1 = "method1"

        def _setup(meth):
            def _hook(iface, method, response):
                self.assertIsInstance(iface, interfaces.Interface)
                self.assertIsInstance(method, interfaces.Method)
                self.assertIsInstance(response, zerojson.Response)
                response.result = {"replaced": response.result}
                return response
            meth.__method__.posthooks.append(_hook)
            return meth

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @_setup
            @pycom.method(meth1)
            def m1(self2, request):
                self.assertEqual(request.args, 42)
                return 100500

        instance = InterfaceWithMethods()
        response = instance.m1.__method__.call(instance.__interface__,
            FakeRequest(args=42))
        self.assertDictEqual(response.result, {"replaced": 100500})


class LocalComponentTest(BaseTest, unittest.TestCase):

    def testCallExisting(self):
        iface = "test.test_components.LocalComponentTest.testCallExisting"
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

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertIs(component.invoke(meth1, args=testObject1), testObject2)

    def testCallImplicit(self):
        iface = "test.test_components.LocalComponentTest.testCallImplicit"
        testObject1 = object()
        testObject2 = object()

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method
            def method1(self, request):
                assert self.__interface__.name == iface
                assert request.args is testObject1
                return testObject2

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertIs(component.invoke("method1", args=testObject1),
            testObject2)

    def testContextPresent(self):
        iface = "test.test_components.LocalComponentTest.testContextPresent"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method
            def method1(self, request):
                assert isinstance(request.context(), pycom.ProxyContext)
                return True

        component = InterfaceWithMethods().__interface__
        self.assertTrue(component.invoke("method1"))

    def testIncomingAttachment(self):
        iface = "test.test_components.LocalComponentTest.testIncomingAttachment"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method
            def method1(self, request):
                return request.attachment

        component = InterfaceWithMethods().__interface__
        self.assertEqual(component.invoke("method1", attachment=b"Hello"),
            b"Hello")

    def testOutgoingAttachment(self):
        iface = "test.test_components.LocalComponentTest.testOutgoingAttachment"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method
            def method1(self, request):
                return request.response(42, attachment=b"Bye")

        component = InterfaceWithMethods().__interface__
        self.assertEqual(component.invoke("method1"), (42, b"Bye"))

    def testCallWithResponse(self):
        iface = "test.test_components.LocalComponentTest.testCallWithResponse"
        meth1 = "method1"
        testObject1 = object()
        testObject2 = object()

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request):
                assert self.__interface__.name == iface
                assert request.args is testObject1
                return request.response(testObject2)

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertIs(component.invoke(meth1, args=testObject1), testObject2)

    def testCallAddedInRT(self):
        iface = "test.test_components.LocalComponentTest.testCallAddedInRT"
        meth1 = "method1"
        testObject1 = object()
        testObject2 = object()

        @pycom.interface(iface)
        class InterfaceWithMethods(object): pass

        def meth1_impl(self, request):
            assert request.args is testObject1
            return request.response(testObject2)

        InterfaceWithMethods.__interface__.register_method(
            pycom.method(meth1, body=meth1_impl))

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertIs(component.invoke(meth1, args=testObject1), testObject2)

    def testCallNonExisting(self):
        iface = "test.test_components.LocalComponentTest.testCallNonExisting"
        meth1 = "method1"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request): pass  # pragma: no cover

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertRaises(pycom.MethodNotFound,
            component.invoke, "banana!")

    def testCallWrongName(self):
        iface = "test.test_components.LocalComponentTest.testCallWrongName"
        meth1 = "method1"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request): pass  # pragma: no cover

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertRaises(pycom.MethodNotFound, component.invoke, "m1")


class ArgumentsTest(BaseTest, unittest.TestCase):

    def testRequiredOnly(self):
        iface = "test.test_interfaces.ArgumentsTest.testRequiredOnly"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth)
            def meth1(self, request, arg1, arg2):
                return [arg1, arg2]

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke(meth, {"arg1": 1, "arg2": 2}),
            [1, 2])
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_interfaces.ArgumentsTest.testRequiredOnly.method1",
            component.invoke, meth,
            {"arg2": 2})
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_interfaces.ArgumentsTest.testRequiredOnly.method1",
            component.invoke, meth,
            42)

    def testOptionalOnly(self):
        iface = "test.test_interfaces.ArgumentsTest.testOptionalOnly"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth)
            def meth1(self, request, arg1=100500, arg2=100501):
                return [arg1, arg2]

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke(meth, {"arg1": 1, "arg2": 2}),
            [1, 2])
        self.assertEqual(component.invoke(meth, {"arg2": 2}),
            [100500, 2])
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_interfaces.ArgumentsTest.testOptionalOnly.method1",
            component.invoke, meth,
            42)
        self.assertEqual(component.invoke(meth),
            [100500, 100501])

    def testResults(self):
        iface = "test.test_interfaces.ArgumentsTest.testResults"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth, results=("res1", "res2"))
            def meth1(self, request):
                return 1, 2

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke(meth),
            {"res1": 1, "res2": 2})

    def testOneResult(self):
        iface = "test.test_interfaces.ArgumentsTest.testOneResult"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth, results=("res1",))
            def meth1(self, request):
                return 0

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke(meth),
            {"res1": 0})

    def testImplicitWResults(self):
        iface = "test.test_components.ArgumentsTest.testImplicitWResults"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(results=("res1",))
            def method1(self, request):
                return 0

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke("method1"),
            {"res1": 0})

    def testBadInterface(self):
        iface = "test.test_interfaces.ArgumentsTest.testBadInterface"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth, results=("res1", "res2"))
            def meth1(self, request):
                return 0

        component = SimpleInterface.__interface__
        self.assertRaises(RuntimeError, component.invoke, meth)

    def testBadInterface2(self):
        iface = "test.test_interfaces.ArgumentsTest.testBadInterface2"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth, results=("res1", "res2"))
            def meth1(self, request):
                return 0, 1, 2

        component = SimpleInterface.__interface__
        self.assertRaises(RuntimeError, component.invoke, meth)

    def testAllArguments(self):
        iface = "test.test_interfaces.ArgumentsTest.testAllArguments"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(meth)
            def meth1(self, request, arg0, arg1=100500, arg2=42):
                return [arg0, arg1, arg2]

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke(meth,
            {"arg0": 0, "arg1": 1, "arg2": 2}),
            [0, 1, 2])
        self.assertEqual(component.invoke(meth, {"arg0": 0}),
            [0, 100500, 42])
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_interfaces.ArgumentsTest.testAllArguments.method1",
            component.invoke, meth,
            {"arg2": 2})
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_interfaces.ArgumentsTest.testAllArguments.method1",
            component.invoke, meth,
            42)


class TestAttachmentsInfo(BaseTest, unittest.TestCase):

    def testNo(self):
        iface = "test.test_interfaces.TestAttachmentsInfo.testNo"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method
            def method1(self, request): pass  # pragma: no cover

        component = SimpleInterface.__interface__
        method = component.methods["method1"]
        self.assertEqual(method.attachments, (None, None))

    def testBoth(self):
        iface = "test.test_interfaces.TestAttachmentsInfo.testBoth"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(attachments=("inc", "out"))
            def method1(self, request): pass  # pragma: no cover

        component = SimpleInterface.__interface__
        method = component.methods["method1"]
        self.assertEqual(method.attachments, ("inc", "out"))

    def testCallIncoming(self):
        iface = "test.test_interfaces.TestAttachmentsInfo.testCallIncoming"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(attachments=("inc", None))
            def method1(self, request, inc):
                return inc.decode("utf-8")

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke("method1", attachment=b"Hello"),
            "Hello")

    def testCallOutgoing(self):
        iface = "test.test_interfaces.TestAttachmentsInfo.testCallOutgoing"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(results=("num", "out"), attachments=(None, "out"))
            def method1(self, request, num):
                return num, bytes(str(num).encode())

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke("method1", args=dict(num=42)),
            (dict(num=42), b"42"))

    def testCallOutgoing2(self):
        iface = "test.test_interfaces.TestAttachmentsInfo.testCallOutgoing2"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @pycom.method(results=("out",), attachments=(None, "out"))
            def method1(self, request, num):
                return bytes(str(num).encode())

        component = SimpleInterface.__interface__
        self.assertEqual(component.invoke("method1", args=dict(num=42)),
            (dict(), b"42"))


class IntrospectionTest(BaseTest, unittest.TestCase):

    maxDiff = None

    def testFullInterface(self):
        iface = "test.test_interfaces.IntrospectionTest.testFullInterface"
        meth1 = "method1"
        meth2 = "method2"

        @pycom.interface(iface)
        class InterfaceWithMethods(pycom.Service):
            "My Demo Service"

            @pycom.method(meth1)
            def m1(self, request, arg1, arg2=None, arg3=0):
                "My Demo Method"
                pass # pragma: no cover

            @pycom.method(meth2, results=("res1", "res2"))
            def m2(self, request): pass # pragma: no cover

        component = InterfaceWithMethods.__interface__
        self.assertEqual(
            component.invoke(constants.GENERIC_METHOD_INTROSPECT), {
                "name": iface,
                "methods": {
                    constants.GENERIC_METHOD_INTROSPECT: {
                        "required_arguments": [],
                        "optional_arguments": [],
                        "results": ["name", "methods", "docstring", "data"],
                        "docstring":
                            "Provides introspection information for a service.",
                        "attachments": {
                            "incoming": None,
                            "outgoing": None
                        }
                    },
                    meth1: {
                        "required_arguments": ["arg1"],
                        "optional_arguments": ["arg2", "arg3"],
                        "results": [],
                        "docstring": "My Demo Method",
                        "attachments": {
                            "incoming": None,
                            "outgoing": None
                        }
                    },
                    meth2: {
                        "required_arguments": [],
                        "optional_arguments": [],
                        "results": ["res1", "res2"],
                        "docstring": None,
                        "attachments": {
                            "incoming": None,
                            "outgoing": None
                        }
                    }
                },
                "docstring": "My Demo Service",
                "data": {}
        })

    def testViaMethod(self):
        iface = "test.test_interfaces.IntrospectionTest.testViaMethod"
        meth1 = "method1"
        meth2 = "method2"

        @pycom.interface(iface)
        class InterfaceWithMethods(pycom.Service):
            "My Demo Service"

            @pycom.method(meth1)
            def m1(self, request, arg1, arg2=None, arg3=0):
                "My Demo Method"
                pass # pragma: no cover

            @pycom.method(meth2, results=("res1", "res2"))
            def m2(self, request): pass # pragma: no cover

        component = InterfaceWithMethods.__interface__
        self.assertEqual(
            component.introspect(),
            component.invoke(constants.GENERIC_METHOD_INTROSPECT))

    def testIntrospectionData(self):
        iface = "test.test_interfaces.IntrospectionTest.testIntrospectionData"

        @pycom.interface(iface)
        class InterfaceWithMethods(pycom.Service):

            introspection_data = {
                "x": None
            }

        component = InterfaceWithMethods.__interface__
        self.assertEqual(
            component.invoke(constants.GENERIC_METHOD_INTROSPECT)["data"], {
                "x": None
            })

    def testWrongIntrospectionData(self):
        iface = "test.test_interfaces.IntrospectionTest.testIntrospectionData"

        def _check():
            @pycom.interface(iface)
            class InterfaceWithMethods(pycom.Service):

                introspection_data = 42

        self.assertRaises(TypeError, _check)


class AuthBaseTest(BaseTest):

    def setUp(self):
        super(AuthBaseTest, self).setUp()

        @pycom.interface(pycom.constants.AUTH_INTERFACE,
            authentication="never")
        class DummyAuthenticator(object):

            @pycom.method(pycom.constants.AUTH_METHOD_AUTHENTICATE,
                results=("token",))
            def authenticate(self, request, user, credentials):
                if user == "valid" and credentials == "password":
                    return "123456"
                else:
                    raise pycom.AccessDenied("invalid user")

            @pycom.method(pycom.constants.AUTH_METHOD_VALIDATE,
                results=("name", "roles"))
            def validate(self, request, token):
                if token == "123456":
                    return "valid", []
                else:
                    raise pycom.AccessDenied("invalid token")

        self.service = DummyAuthenticator.__interface__

        def locate2(name):
            self.assertEqual(name, pycom.constants.AUTH_INTERFACE)
            return self.service

        self.locate = locate2

        self.tested = pycom.Context()
        self.tested.locate = locate2


class TestServiceWithAuth(AuthBaseTest, unittest.TestCase):

    def testContextFactory(self):
        @pycom.interface(pycom.constants.NS_INTERFACE)
        class Nameserver(pycom.Service):

            @pycom.method
            def start(self2, request):
                ctx = request.context()
                ctx.locate = self.locate
                return ctx.nameserver().finish()

            @pycom.method
            def finish(self2, request):
                return request.extensions[pycom.constants.AUTH_EXTENSION]

        self.tested.authenticate("valid", "password")
        component = self.tested.nameserver()
        with replacer(nsclient, "Context", lambda: self.tested):
            self.assertEqual(component.invoke("start"), "123456")


class TestCheckRequiredAuth(AuthBaseTest, unittest.TestCase):

    def testNoPolicy(self):
        @pycom.interface(pycom.constants.NS_INTERFACE)
        class Nameserver(pycom.Service):

            @pycom.method
            def test(self2, request): pass

        component = self.tested.nameserver()
        self.assertEqual(component.invoke("test"), None)

    def testPolicyRequiredFailure(self):
        @pycom.interface(pycom.constants.NS_INTERFACE)
        class Nameserver(pycom.Service):

            @pycom.method
            def test(self2, request): pass  # pragma: no cover

        pycom.configure(authentication=dict(policy="required"))
        component = self.tested.nameserver()
        self.assertRaises(pycom.AccessDenied, component.invoke, "test")

    def testPolicyRequiredFailure2(self):
        @pycom.interface(pycom.constants.NS_INTERFACE,
            authentication="required")
        class Nameserver(pycom.Service):

            @pycom.method
            def test(self2, request): pass  # pragma: no cover

        component = self.tested.nameserver()
        self.assertRaises(pycom.AccessDenied, component.invoke, "test")

    def testPolicyNeverOk(self):
        @pycom.interface(pycom.constants.NS_INTERFACE, authentication="never")
        class Nameserver(pycom.Service):

            @pycom.method
            def test(self2, request): pass  # pragma: no cover

        pycom.configure(authentication=dict(policy="required"))
        component = self.tested.nameserver()
        self.assertEqual(component.invoke("test"), None)

    def testPolicyRequiredOk(self):
        @pycom.interface(pycom.constants.NS_INTERFACE)
        class Nameserver(pycom.Service):

            @pycom.method
            def test(self2, request): pass

        pycom.configure(authentication=dict(policy="required"))
        self.tested.authenticate("valid", "password")
        component = self.tested.nameserver()
        with replacer(nsclient, "Context", lambda: self.tested):
            self.assertEqual(component.invoke("test"), None)
