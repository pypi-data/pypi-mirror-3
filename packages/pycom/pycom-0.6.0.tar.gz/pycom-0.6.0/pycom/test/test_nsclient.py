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

"""Tests for pycom.nsclient."""

import random
import threading

import zmq

import pycom
import zerojson
from pycom import base, constants, interfaces, nsclient
from zerojson import call, common

from zerojson.testing import unittest, replacer
from .test_interfaces import BaseTest as InterfacesBaseTest, AuthBaseTest


class BaseTest(InterfacesBaseTest):

    timeout = 3

    def setUp(self):
        super(BaseTest, self).setUp()
        pycom.configure(nameserver="local")

    def tearDown(self):
        super(BaseTest, self).tearDown()

class LocalNSTest(BaseTest, unittest.TestCase):

    def testErrorOnAbsentNameserver(self):
        self.assertRaises(zerojson.ServiceNotFound,
            pycom.Context().nameserver)

    def testErrorOnMalformedNS(self):
        pycom.configure(nameserver="host:unknown.unknown")

        @pycom.interface(constants.NS_INTERFACE)
        class Nameserver(object): pass

        self.assertRaises(base.ConfigurationError,
            pycom.Context().nameserver)

    def testNsInThisService(self):
        @pycom.interface(constants.NS_INTERFACE)
        class Nameserver(object): pass

        ctx = pycom.Context()
        ns = ctx.nameserver()
        self.assertIsInstance(ns, pycom.BaseComponent)
        self.assertIsInstance(ns.instance, Nameserver)
        self.assertIs(ns.context, ctx)

    def testCachedNs(self):
        @pycom.interface(constants.NS_INTERFACE)
        class Nameserver(object): pass

        context = pycom.Context()

        ns1 = context.nameserver()
        self.assertIs(ns1, context.nameserver())

        base.interface_registry.clear()
        self.assertIs(ns1, context.nameserver())

    def testNSThreadSafe(self):
        @pycom.interface(constants.NS_INTERFACE)
        class Nameserver(object): pass

        context = pycom.Context()

        ns1 = context.nameserver()
        ns2_l = []

        def _check():
            ns2_l.append(context.nameserver())

        thread = threading.Thread(target=_check)
        thread.start()
        thread.join()

        self.assertIsNot(ns1, ns2_l[0])

def fake_container(context, event, addr, event2, handler):
    # To be executed in a separate thread
    sock = context.socket(zmq.REP)
    sock.bind(addr)
    event2.set()
    call_command = call.CallCommand()

    while not event.is_set():
        if not sock.poll(timeout=10):
            continue

        items = sock.recv_multipart()
        cmd, body = items[:2]
        assert cmd == zerojson.constants.PROTO_CMD_CALL

        request = call_command.request_from_wire(body)
        request.attachment = items[2] if len(items) > 2 else None
        if request.method == "send me attachment":
            sock.send_multipart([zerojson.constants.PROTO_STATUS_SUCCESS,
                call_command.response_to_wire(request.response({})),
                b"Welcome"])
        else:
            sock.send_multipart([zerojson.constants.PROTO_STATUS_SUCCESS,
                call_command.response_to_wire(handler(request))])

    sock.close()


def ns_handler(request):
    assert request.interface == constants.NS_INTERFACE
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT, "att-demo")

    if request.method == constants.NS_METHOD_STAT:
        return request.response({})
    elif request.method == "att-demo":
        return request.response(request.attachment.decode("utf-8"))
    else:
        return zerojson.Response(request,
                code=zerojson.constants.ERROR_SERVICE_NOT_FOUND)


class RemoteNSTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(RemoteNSTest, self).setUp()

        addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(common.context, self.event, addr, event2,
            ns_handler))
        self.thread.start()
        event2.wait()

    def tearDown(self):
        self.event.set()
        del self.event
        self.thread.join()
        del self.thread

        super(RemoteNSTest, self).tearDown()

    def testNS(self):
        ns = pycom.Context().nameserver()
        self.assertDictEqual(ns.invoke(constants.NS_METHOD_STAT), {})
        self.assertRaises(pycom.RemoteError,
            ns.invoke, constants.NS_METHOD_LOCATE, {
                "interface": "org.pycom.test_nsclient.NON-EXISTING"
            })

    def testNSContextManager(self):
        with pycom.Context().nameserver() as ns:
            self.assertDictEqual(ns.invoke(constants.NS_METHOD_STAT), {})
            self.assertRaises(pycom.RemoteError,
                ns.invoke, constants.NS_METHOD_LOCATE, {
                    "interface": "org.pycom.test_nsclient.NON-EXISTING"
                })

    def testIncomingAttachment(self):
        ns = pycom.Context().nameserver()
        self.assertEqual(ns.invoke("att-demo", attachment=b"Hello"), "Hello")

    def testOutgoingAttachment(self):
        ns = pycom.Context().nameserver()
        self.assertEqual(ns.invoke("send me attachment"), ({}, b"Welcome"))

    def testUnknownNS(self):
        context = pycom.Context(nameserver="ipc://pycom/banana!")
        with replacer(zerojson.constants, "PROTO_DEFAULT_TIMEOUT", 100):
            self.assertRaises(zerojson.ServiceNotFound, context.nameserver)

    def testUnknownNS2(self):
        context = pycom.Context(nameserver="inproc://pycom/banana!")
        with replacer(zerojson.constants, "PROTO_DEFAULT_TIMEOUT", 100):
            self.assertRaises(zerojson.ServiceNotFound, context.nameserver)

    def testLocateError(self):
        self.assertRaises(zerojson.ServiceNotFound,
            pycom.Context().locate, "org.pycom.test_nsclient.NON-EXISTING")


class RemoteNSTestContext(BaseTest, unittest.TestCase):

    def setUp(self):
        super(RemoteNSTestContext, self).setUp()

        self.addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(common.context, self.event, self.addr, event2,
            ns_handler))
        self.thread.start()
        event2.wait()

    def tearDown(self):
        self.event.set()
        del self.event
        self.thread.join()
        del self.thread
        self.context = None

        super(RemoteNSTestContext, self).tearDown()

    def testNS(self):
        self.context = pycom.Context(nameserver=self.addr)
        ns = self.context.nameserver()
        self.assertDictEqual(ns.invoke(constants.NS_METHOD_STAT), {})
        self.assertRaises(pycom.RemoteError,
            ns.invoke, constants.NS_METHOD_LOCATE, {
                "interface": "org.pycom.test_nsclient.NON-EXISTING"
            })

    def testLocate(self):
        self.context = pycom.Context(nameserver=self.addr)
        self.assertRaises(zerojson.ServiceNotFound,
            self.context.locate, "org.pycom.test_nsclient.NON-EXISTING")


def ns_handler_w_error(request):
    assert request.interface == constants.NS_INTERFACE
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT)

    if request.method == constants.NS_METHOD_STAT:
        return request.response({})
    else:
        return zerojson.Response(request, code=100500)


class LocateFailureTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(LocateFailureTest, self).setUp()

        addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(common.context, self.event, addr, event2,
            ns_handler_w_error))
        self.thread.start()
        event2.wait()

    def tearDown(self):
        self.event.set()
        del self.event
        self.thread.join()
        del self.thread

        super(LocateFailureTest, self).tearDown()

    def testUnknownError(self):
        with self.assertRaises(pycom.RemoteError) as cm:
            pycom.Context().locate("org.pycom.test_nsclient.NON-EXISTING")
        self.assertEqual(cm.exception.code, 100500)


def ns_handler2(request):
    assert request.interface == constants.NS_INTERFACE
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT)

    if request.method == constants.NS_METHOD_STAT:
        return request.response({})
    else:
        if request.args["interface"] == "iface.name":
            assert request.args.get("service") is None
            return request.response({"address": "ipc://test_nsclient_h2"})
        elif request.args["interface"] == "iface.name2":
            assert request.args["service"] == "service.name2"
            return request.response({"address": "ipc://test_nsclient_h2"})
        else:
            return zerojson.Response(request,
                code=zerojson.constants.ERROR_SERVICE_NOT_FOUND)


class LocateTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(LocateTest, self).setUp()

        self.addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=self.addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(common.context, self.event, self.addr, event2,
            ns_handler2))
        self.thread.start()
        event2.wait()

    def tearDown(self):
        self.event.set()
        del self.event
        self.thread.join()
        del self.thread

        super(LocateTest, self).tearDown()

    def testConnect(self):
        ctx = pycom.Context()
        component = ctx.connect(self.addr, constants.NS_INTERFACE)
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertEqual(component.invoke(constants.NS_METHOD_STAT), {})
        self.assertIs(component.context, ctx)

    def testLocate(self):
        ctx = pycom.Context()
        component = ctx.locate("iface.name")
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertEqual(component.name, "iface.name")
        self.assertIsInstance(component._wrapped, zerojson.Client)
        self.assertIs(component.context, ctx)

    def testLocateContextManager(self):
        with pycom.Context().locate("iface.name") as component:
            self.assertIsInstance(component, pycom.BaseComponent)
            self.assertEqual(component.name, "iface.name")
            self.assertIsInstance(component._wrapped, zerojson.Client)

    def testLocateWService(self):
        component = pycom.Context().locate("iface.name2",
            service_name="service.name2")
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertEqual(component.name, "iface.name2")
        self.assertIsInstance(component._wrapped, zerojson.Client)

    def testLocateFail(self):
        self.assertRaises(zerojson.ServiceNotFound,
            pycom.Context().locate, "org.pycom.test_nsclient.NON-EXISTING")


class ContextHooksTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(ContextHooksTest, self).setUp()

        @pycom.interface(constants.NS_INTERFACE)
        class Nameserver(object):

            @pycom.method
            def stat(self2, request):
                return request.args

    def testPrehook(self):
        def _hook(comp, request):
            self.assertIsInstance(comp, base.BaseComponent)
            self.assertIsInstance(request, zerojson.Request)
            request.args = {"input": request.args}
            return request

        ctx = pycom.Context()
        ctx.prehooks.append(_hook)
        self.assertEqual(ctx.nameserver().invoke("stat", args=42),
            {"input": 42})

    def testPosthook(self):
        def _hook(comp, response):
            self.assertIsInstance(comp, base.BaseComponent)
            self.assertIsInstance(response, zerojson.Response)
            response.result = {"output": response.result}
            return response

        ctx = pycom.Context()
        ctx.posthooks.append(_hook)
        self.assertEqual(ctx.nameserver().invoke("stat", args=42),
            {"output": 42})


class TestAuthTokens(AuthBaseTest, unittest.TestCase):

    def setUp(self):
        super(TestAuthTokens, self).setUp()

    def testGetValidToken(self):
        self.assertEqual(self.tested._get_token("valid", "password"),
            "123456")

    def testGetInvalidToken(self):
        self.assertRaises(pycom.AccessDenied, self.tested._get_token,
            "invalid", "password")
        self.assertRaises(pycom.AccessDenied, self.tested._get_token,
            "valid", "invalid")

    def testCheckValidToken(self):
        self.assertEqual(self.tested._check_token("123456"),
            {"name": "valid", "roles": []})

    def testCheckInvalidToken(self):
        self.assertRaises(pycom.AccessDenied, self.tested._check_token,
            "invalid")


class TestAuthContextHooks(AuthBaseTest, unittest.TestCase):

    def setUp(self):
        super(TestAuthContextHooks, self).setUp()

        @pycom.interface(pycom.constants.NS_INTERFACE)
        class Nameserver(object):

            @pycom.method
            def demo(self, request):
                return request.extensions[pycom.constants.AUTH_EXTENSION]

    def testContextAuthenticate(self):
        ctx = self.tested
        ctx.authenticate("valid", "password")
        self.assertEqual(ctx.nameserver().invoke("demo"), "123456")
        self.assertEqual(ctx.user_info(), {"name": "valid", "roles": []})

    def testAuthenticationByToken(self):
        ctx = self.tested
        ctx.authenticate(token="123456")
        self.assertEqual(ctx.nameserver().invoke("demo"), "123456")
        self.assertEqual(ctx.user_info(), {"name": "valid", "roles": []})

    def testNonAuthContext(self):
        self.assertIs(self.tested.user_info(), None)
