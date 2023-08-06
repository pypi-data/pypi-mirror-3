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
from pycom import constants, exceptions, interfaces, nsclient, protocol

from .utils import unittest, Replacer
from .test_interfaces import BaseTest as InterfacesBaseTest

class BaseTest(InterfacesBaseTest):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.oldNS = getattr(nsclient._tls, "ns_component", None)
        nsclient._tls.ns_component = None
        pycom.configure(nameserver="local")

    def tearDown(self):
        nsclient._tls.ns_component = self.oldNS
        super(BaseTest, self).tearDown()

class LocalNSTest(BaseTest, unittest.TestCase):

    def testErrorOnAbsentNameserver(self):
        self.assertRaises(exceptions.ServiceNotFound, pycom.nameserver)

    def testErrorOnMalformedNS(self):
        pycom.configure(nameserver="host:unknown.unknown")

        @pycom.interface(constants.IFACE_NAMESERVER)
        class Nameserver(object): pass

        self.assertRaises(exceptions.ConfigurationError, pycom.nameserver)

    def testNsInThisService(self):
        @pycom.interface(constants.IFACE_NAMESERVER)
        class Nameserver(object): pass

        ns = pycom.nameserver()
        self.assertIsInstance(ns, pycom.BaseComponent)
        self.assertIsInstance(ns.instance, Nameserver)

    def testCachedNs(self):
        @pycom.interface(constants.IFACE_NAMESERVER)
        class Nameserver(object): pass

        ns1 = pycom.nameserver()
        self.assertIs(ns1, pycom.nameserver())

        interfaces.registry.clear()
        self.assertIs(ns1, pycom.nameserver())


def fake_container(context, event, addr, event2, handler):
    # To be executed in a separate thread
    sock = context.socket(zmq.REP)
    sock.bind(addr)
    event2.set()

    while not event.is_set():
        if not sock.poll(timeout=10):
            continue

        cmd, body = sock.recv_multipart()
        assert cmd == constants.PROTO_CMD_CALL

        request = protocol.request_from_wire(body)
        sock.send_multipart([constants.PROTO_STATUS_SUCCESS,
            protocol.response_to_wire(*handler(request))])

    sock.close()


def ns_handler(request):
    assert request.interface == constants.IFACE_NAMESERVER
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT)

    if request.method == constants.NS_METHOD_STAT:
        return 0, None, {}, None
    else:
        return constants.ERROR_SERVICE_NOT_FOUND, None, None, None


class RemoteNSTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(RemoteNSTest, self).setUp()

        addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(protocol.context, self.event, addr, event2,
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
        ns = pycom.nameserver()
        self.assertDictEqual(ns.invoke(constants.NS_METHOD_STAT), {})
        self.assertRaises(exceptions.RemoteError,
            ns.invoke, constants.NS_METHOD_LOCATE, {
                "interface": "org.pycom.test_nsclient.NON-EXISTING"
            })

    def testUnknownNS(self):
        pycom.configure(nameserver="ipc://pycom/banana!")
        with Replacer(constants, "PROTO_DEFAULT_TIMEOUT", 100):
            self.assertRaises(exceptions.ServiceNotFound, pycom.nameserver)

    def testUnknownNS2(self):
        pycom.configure(nameserver="inproc://pycom/banana!")
        with Replacer(constants, "PROTO_DEFAULT_TIMEOUT", 100):
            self.assertRaises(exceptions.ServiceNotFound, pycom.nameserver)

    def testLocateError(self):
        self.assertRaises(exceptions.ServiceNotFound,
            pycom.locate, "org.pycom.test_nsclient.NON-EXISTING")


def ns_handler_w_error(request):
    assert request.interface == constants.IFACE_NAMESERVER
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT)

    if request.method == constants.NS_METHOD_STAT:
        return 0, None, {}, None
    else:
        return 100500, None, None, None


class LocateFailureTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(LocateFailureTest, self).setUp()

        addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(protocol.context, self.event, addr, event2,
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
        with self.assertRaises(exceptions.RemoteError) as cm:
            pycom.locate("org.pycom.test_nsclient.NON-EXISTING")
        self.assertEqual(cm.exception.code, 100500)


def ns_handler2(request):
    assert request.interface == constants.IFACE_NAMESERVER
    assert request.method in (constants.NS_METHOD_LOCATE,
        constants.NS_METHOD_STAT)

    if request.method == constants.NS_METHOD_STAT:
        return 0, None, {}, None
    else:
        if request.args["interface"] == "iface.name":
            assert request.args.get("service") is None
            return 0, None, {"address": "ipc://test_nsclient_h2"}, None
        elif request.args["interface"] == "iface.name2":
            assert request.args["service"] == "service.name2"
            return 0, None, {"address": "ipc://test_nsclient_h2"}, None
        else:
            return constants.ERROR_SERVICE_NOT_FOUND, None, None, None


class LocateTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(LocateTest, self).setUp()

        addr = "inproc://test_nsclient_ns-%d" % random.randint(0, 100000)
        pycom.configure(nameserver=addr)

        self.event = threading.Event()
        event2 = threading.Event()

        self.thread = threading.Thread(target=fake_container,
            args=(protocol.context, self.event, addr, event2,
            ns_handler2))
        self.thread.start()
        event2.wait()

    def tearDown(self):
        self.event.set()
        del self.event
        self.thread.join()
        del self.thread

        super(LocateTest, self).tearDown()

    def testLocate(self):
        component = pycom.locate("iface.name")
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertEqual(component.iface, "iface.name")
        self.assertIsInstance(component.socket, zmq.Socket)

    def testLocateWService(self):
        component = pycom.locate("iface.name2", service_name="service.name2")
        self.assertIsInstance(component, pycom.BaseComponent)
        self.assertEqual(component.iface, "iface.name2")
        self.assertIsInstance(component.socket, zmq.Socket)

    def testLocateFail(self):
        self.assertRaises(exceptions.ServiceNotFound,
            pycom.locate, "org.pycom.test_nsclient.NON-EXISTING")
