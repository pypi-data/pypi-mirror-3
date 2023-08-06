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

"""Tests for pycom.launcher and pycom.zerojson."""

import io
import random
import sys
import threading
import time
import uuid

import six
from six import StringIO

import pycom
import pycom.apps.nameserver
from pycom import base, constants, nsclient, utils
from pycom.zerojson import call, client as protocol

from .utils import unittest, Replacer
from .test_nsclient import BaseTest


class MainTest(BaseTest, unittest.TestCase):

    def setUp(self):
        super(MainTest, self).setUp()
        self.oldConf = base.configuration.copy()
        base.configuration.clear()

        nsclient._tls.ns_component = \
            pycom.apps.nameserver.NameServer().__interface__

    def tearDown(self):
        base.configuration.clear()
        base.configuration.update(self.oldConf)
        super(MainTest, self).tearDown()

    def testService(self):
        iface = "test.test_launcher.MainTest.testService"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            self.assertDictEqual(component.invoke(meth, [1, 2, 3]),
                {"input": [1, 2, 3]})

        self._testService(iface, meth, _testMethod, _check, self)

    def testConfigurationError(self):
        pycom.configure(service="/test/test_launcher")
        self.assertRaisesRegexp(pycom.ConfigurationError, "address",
            pycom.main)

    def testUnknownInterface(self):
        iface = "test.test_launcher.MainTest.testUnknownInterface"
        meth = "test_method"

        def _check(address, self):
            wrong_iface = iface + "/banana!"
            component = protocol.RemoteComponent(address, wrong_iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Unsupported interface: %s" % wrong_iface) as context:
                component.invoke(meth)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    def testUnknownMethod(self):
        iface = "test.test_launcher.MainTest.testUnknownMethod"
        meth = "test_method"

        def _check(address, self):
            wrong_meth = meth + "/banana!"
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.MethodNotFound,
                    "Method '%s' not found in interface %s" %
                    (wrong_meth, iface)) as context:
                component.invoke(wrong_meth)
            self.assertEqual(context.exception.code,
                constants.ERROR_METHOD_NOT_FOUND)

        self._testService(iface, meth, _testMethod, _check, self)

    def testKnownException(self):
        iface = "test.test_launcher.MainTest.testKnownException"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "test BadRequest") as context:
                component.invoke(meth)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethodWithKnownError, _check, self)

    def testUnknownException(self):
        iface = "test.test_launcher.MainTest.testUnknownException"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Unknown error during request") as context:
                component.invoke(meth)
            self.assertEqual(context.exception.code,
                constants.ERROR_UNKNOWN)

        self._testService(iface, meth, _testMethodWithUnknownError, _check, self)

    def testSession(self):
        iface = "test.test_launcher.MainTest.testSession"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            self.assertEqual(component.invoke(meth, 42), 42)
            self.assertEqual(component.invoke(meth, 100500), 100500)
            self.assertEqual(component.invoke(meth), 100500)

        self._testService(iface, meth, _testSession, _check, self)

    def testUnknownCommand(self):
        iface = "test.test_launcher.MainTest.testUnknownCommand"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Unknown command") as context:
                message = component._send_message(b"banana!", b"{}", 1000)[1]
                self.assertTrue(message)
                call.CallCommand().response_from_wire(message)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    def testWrongJSON(self):
        iface = "test.test_launcher.MainTest.testWrongJSON"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Cannot decode response") as context:
                message = component._send_message(constants.PROTO_CMD_CALL,
                    b"!!!", 1000)[1]
                call.CallCommand().response_from_wire(message)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    def testMissingFields(self):
        iface = "test.test_launcher.MainTest.testMissingFields"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Field [a-z]+ is required") as context:
                message = component._send_message(constants.PROTO_CMD_CALL,
                    b"{}", 1000)[1]
                call.CallCommand().response_from_wire(message)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    def testWrongUTF8(self):
        iface = "test.test_launcher.MainTest.testWrongUTF8"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Invalid encoding, expected UTF-8") as context:
                message = component._send_message(constants.PROTO_CMD_CALL,
                    b"{\"v1\": \"\xff\xff\"}", 1000)[1]
                call.CallCommand().response_from_wire(message)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    def testWrongPartsCount(self):
        iface = "test.test_launcher.MainTest.testWrongPartsCount"
        meth = "test_method"

        def _check(address, self):
            component = protocol.RemoteComponent(address, iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Expected two parts, got 3") as context:
                message = component._send_message(constants.PROTO_CMD_CALL,
                    call.CallCommand().request_to_wire(iface, meth, {}),
                    1000, attachment=b"")[1]
                call.CallCommand().response_from_wire(message)
            self.assertEqual(context.exception.code,
                constants.ERROR_BAD_REQUEST)

        self._testService(iface, meth, _testMethod, _check, self)

    # Private

    def _testService(self, iface, meth, meth_body, call, *args, **kw):
        @pycom.interface(iface)
        class Service(object):

            @pycom.method(meth)
            def test_method(self, request):
                return meth_body(request)

        address = "ipc:///tmp/pycom_test_launcher-%d" % uuid.uuid4().int

        def _check():
            try:
                call(address, *args, **kw)
            finally:
                pycom.ioloop().add_callback(pycom.ioloop().stop)

        threading.Thread(target=_check).start()

        pycom.configure(address=address, service="/test/test_launcher")
        pycom.main()


_testMethod = lambda request: {"input": request.args}

def _testMethodWithKnownError(request):
    raise pycom.BadRequest("test BadRequest")

def _testMethodWithUnknownError(request):
    raise TypeError("test TypeError")

def _testSession(request):
    if request.args:
        request.session["test"] = request.args

    return request.session["test"]


class ArgsTest(unittest.TestCase):

    def setUp(self):
        super(ArgsTest, self).setUp()
        self.oldConf = base.configuration.copy()
        base.configuration.clear()

    def tearDown(self):
        base.configuration.clear()
        base.configuration.update(self.oldConf)
        super(ArgsTest, self).tearDown()

    def testFailEmptyArgs(self):
        with Replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, pycom.main, [])

    def testFailEmptyAddress(self):
        with Replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, pycom.main, ["sys", "-a"])

    def testGeneratedService(self):
        address = "ipc:///tmp/pycom_test_launcher-%d" % uuid.uuid4().int

        pycom.ioloop().add_callback(pycom.ioloop().stop)
        pycom.main(["sys", "-a", address])

    def testFailUnknownOption(self):
        with Replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, pycom.main, ["sys", "-x"])

    def testCorrectOptions(self):
        address = "ipc:///tmp/pycom_test_launcher-%d" % uuid.uuid4().int

        pycom.ioloop().add_callback(pycom.ioloop().stop)
        pycom.main(["sys", "-a", address, "-s", "/test/test_launcher2"])

    def testNameserverOption(self):
        address = "ipc:///tmp/pycom_test_launcher-%d" % uuid.uuid4().int

        def _check():
            try:
                self.assertEqual(base.configuration["nameserver"],
                    "test_ns_vi_cmd")
            finally:
                pycom.ioloop().stop()

        pycom.ioloop().add_callback(_check)
        pycom.main(["sys", "-a", address, "-s", "/test/test_launcher2",
            "-n", "test_ns_vi_cmd"])

    def testUnknownModule(self):
        address = "ipc:///tmp/pycom_test_launcher-%d" % uuid.uuid4().int

        with Replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, pycom.main,
                ["banana!", "-a", address, "-s", "/test/test_launcher2"])
