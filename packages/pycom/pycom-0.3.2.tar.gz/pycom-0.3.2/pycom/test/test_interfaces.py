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

"""Tests for pycom.interfaces."""

import functools
import re

import pycom
from pycom import exceptions, interfaces

from .utils import unittest

class BaseTest(object):

    def setUp(self):
        self.registry_bak = interfaces.registry.copy()
        interfaces.registry.clear()

    def tearDown(self):
        interfaces.registry = self.registry_bak

class DecoratorsTest(BaseTest, unittest.TestCase):

    def testEmptyInterface(self):
        iface = "test.test_interfaces.DecoratorsTest.testEmptyInterface"

        @pycom.interface(iface)
        class EmptyInterface(object): pass

        self.assertIn(iface, interfaces.registry)
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


FakeRequest = functools.partial(pycom.Request, None, None, None)


class HooksTest(BaseTest, unittest.TestCase):

    def testPreHook(self):
        iface = "test.test_interfaces.HooksTest.testPreHook"
        meth1 = "method1"

        def _setup(meth):
            def _hook(iface, method, data):
                self.assertIsInstance(iface, interfaces.Interface)
                self.assertIsInstance(method, interfaces.Method)
                return {"replaced": data}
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
        result = instance.m1.__method__.call(instance.__interface__,
            FakeRequest(42))
        self.assertEqual(result, 100500)

    def testPostHook(self):
        iface = "test.test_interfaces.HooksTest.testPostHook"
        meth1 = "method1"

        def _setup(meth):
            def _hook(iface, method, data):
                self.assertIsInstance(iface, interfaces.Interface)
                self.assertIsInstance(method, interfaces.Method)
                return {"replaced": data}
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
        result = instance.m1.__method__.call(instance.__interface__,
            FakeRequest(42))
        self.assertDictEqual(result, {"replaced": 100500})


class LocalComponentTest(BaseTest, unittest.TestCase):

    def testCallExisting(self):
        iface = "test.test_components.LocalComponentTest.testCall"
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

    def testCallNonExisting(self):
        iface = "test.test_components.LocalComponentTest.testCallNonExisting"
        meth1 = "method1"

        @pycom.interface(iface)
        class InterfaceWithMethods(object):

            @pycom.method(meth1)
            def m1(self, request): pass  # pragma: no cover

        component = InterfaceWithMethods().__interface__
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertRaises(exceptions.MethodNotFound,
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
        self.assertRaises(exceptions.MethodNotFound, component.invoke, "m1")
