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
import functools
import random
import sys
import threading
import time
import uuid

import six
from six import StringIO

import pycom
import pycom.apps.nameserver
import zerojson
from pycom import base, constants, nsclient, utils
from zerojson import call

from zerojson.testing import unittest, AddressGenerationMixin, replacer
from .test_nsclient import BaseTest


class MainTest(BaseTest, AddressGenerationMixin, unittest.TestCase):

    timeout = 3

    def setUp(self):
        super(MainTest, self).setUp()
        AddressGenerationMixin.setUp(self)
        self.oldConf = base.configuration.copy()
        base.configuration.clear()

        self.context = nsclient.Context()
        self.oldNS = nsclient._pop_cached_ns(ctx=self.context)
        self.newNS = pycom.apps.nameserver.NameServer.__interface__
        nsclient._restore_cached_ns(self.newNS, ctx=self.context)
        self.main = functools.partial(pycom.main, client_context=self.context)
        pycom.apps.nameserver.NameServer._registry.clear()
        pycom.apps.nameserver.NameServer._services.clear()

    def tearDown(self):
        self.context = None
        base.configuration.clear()
        base.configuration.update(self.oldConf)
        AddressGenerationMixin.tearDown(self)
        super(MainTest, self).tearDown()

    def testService(self):
        iface = "test.test_launcher.MainTest.testService"
        meth = "test_method"

        def _check(address, self):
            component = nsclient.RemoteComponent(address, iface)
            self.assertDictEqual(component.invoke(meth, [1, 2, 3]),
                {"input": [1, 2, 3]})

        def _testMethod(request):
            return {"input": request.args}

        self._testService(iface, meth, _testMethod, _check, self)

    def testServiceNoSession(self):
        iface = "test.test_launcher.MainTest.testService"
        meth = "test_method"

        def _check(address, self):
            component = nsclient.RemoteComponent(address, iface)
            self.assertEqual(component.invoke(meth), None)

        def _testMethod(request):
            return request.session

        self._testService(iface, meth, _testMethod, _check, self)

    def testServiceWithSession(self):
        iface = "test.test_launcher.MainTest.testService"
        meth = "test_method"

        def _check(address, self):
            component = nsclient.RemoteComponent(address, iface)
            self.assertEqual(component.invoke(meth, 42), 42)
            self.assertEqual(component.invoke(meth), 42)

        def _testMethod(request):
            if request.args:
                request.session["data"] = request.args
            return request.session["data"]

        self._testService(iface, meth, _testMethod, _check, self,
            stateful=True)

    def testFuture(self):
        iface = "test.test_launcher.MainTest.testFuture"
        meth = "test_method"

        def _finish(future):
            future.response({"input": future.request.args})

        def _method(request):
            self.assertEqual(request.interface, iface)
            future = zerojson.Future(request)
            pycom.ioloop().add_callback(functools.partial(_finish, future))
            return future

        def _check(address, self):
            component = nsclient.RemoteComponent(address, iface)
            self.assertDictEqual(component.invoke(meth, [1, 2, 3]),
                {"input": [1, 2, 3]})

        self._testService(iface, meth, _method, _check, self)

    def testConfigurationError(self):
        pycom.configure(service="/test/test_launcher")
        self.assertRaisesRegexp(pycom.ConfigurationError, "address",
            pycom.main)

    def testUnknownInterface(self):
        iface = "test.test_launcher.MainTest.testUnknownInterface"
        meth = "test_method"

        def _check(address, self):
            wrong_iface = iface + "/banana!"
            component = nsclient.RemoteComponent(address, wrong_iface)
            with self.assertRaisesRegexp(pycom.RemoteError,
                    "Unsupported interface: %s" % wrong_iface) as context:
                component.invoke(meth)
            self.assertEqual(context.exception.code,
                zerojson.constants.ERROR_BAD_REQUEST)

        def _testMethod(request): pass  # pragma: no cover

        self._testService(iface, meth, _testMethod, _check, self)

    def testRecreating(self):
        iface = "test.test_launcher.MainTest.testRecreating"
        meth = "test_method"

        @pycom.interface(iface)
        class Service(object):

            @pycom.method(meth)
            def test_method(self, request):
                return request.args

        address = self.genAddress()

        def _check():
            try:
                ctx = pycom.Context()
                nsclient._restore_cached_ns(self.newNS, ctx=ctx)

                # Do not delete these strange-looking loops,
                # they are here to avoid race conditions in this code
                # (nameserver is not thread-safe)

                test_foo = lambda: self.assertEqual(
                    ctx.locate(iface).invoke(meth, args=42), 42)

                for i in range(100):  # pragma: no cover
                    # Wait for registry to be initalized
                    try:
                        test_foo()
                    except pycom.ServiceNotFound:
                        time.sleep(0.01)
                    else:
                        break
                else:  # pragma: no cover
                    test_foo()

                self.assertEqual(ctx.locate(iface).invoke(meth, args=42), 42)
                self.newNS.instance._registry.clear()
                self.newNS.instance._services.clear()
                self.assertRaises(pycom.ServiceNotFound, ctx.locate, iface)

                for i in range(100):  # pragma: no cover
                    # Wait until launcher catches up
                    try:
                        test_foo()
                    except pycom.ServiceNotFound:
                        time.sleep(0.15)
                    else:
                        break
                else:  # pragma: no cover
                    test_foo()

            finally:
                pycom.ioloop().add_callback(pycom.ioloop().stop)

        threading.Thread(target=_check).start()

        pycom.configure(address=address)
        with replacer(constants, "NS_SERVICE_TIMEOUT", 70):
            self.main()

    # Private

    def _testService(self, iface, meth, meth_body, call, *args, **kw):
        @pycom.interface(iface, stateful=kw.pop("stateful", False))
        class Service(object):

            @pycom.method(meth)
            def test_method(self, request):
                return meth_body(request)

        address = self.genAddress()

        ok = [False]

        def _check():
            try:
                call(address, *args, **kw)
                ok[0] = True
            finally:
                pycom.ioloop().add_callback(pycom.ioloop().stop)

        threading.Thread(target=_check).start()

        pycom.configure(address=address)
        self.main()

        self.assertTrue(ok[0], "Test failed, see error above")


class DummyNS(object):

    def invoke(*args, **kwargs): pass


class ArgsTest(AddressGenerationMixin, unittest.TestCase):

    def setUp(self):
        super(ArgsTest, self).setUp()
        self.oldConf = base.configuration.copy()
        base.configuration.clear()
        self.context = nsclient.Context()
        self.oldNS = nsclient._pop_cached_ns(ctx=self.context)
        nsclient._restore_cached_ns(DummyNS(), ctx=self.context)
        self.main = functools.partial(pycom.main, client_context=self.context)

    def tearDown(self):
        self.context = None
        base.configuration.clear()
        base.configuration.update(self.oldConf)
        super(ArgsTest, self).tearDown()

    def testFailEmptyArgs(self):
        with replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, self.main, [])

    def testFailEmptyAddress(self):
        with replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, self.main, ["sys", "-a"])

    def testGeneratedService(self):
        address = self.genAddress()

        pycom.ioloop().add_callback(pycom.ioloop().stop)
        self.main(["sys", "-a", address])

    def testFailUnknownOption(self):
        with replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, self.main, ["sys", "-x"])

    def testCorrectOptions(self):
        address = self.genAddress()

        pycom.ioloop().add_callback(pycom.ioloop().stop)
        self.main(["sys", "-a", address, "-s", "/test/test_launcher2"])

    def testNameserverOption(self):
        address = self.genAddress()

        def _check():
            try:
                self.assertEqual(base.configuration["nameserver"],
                    "test_ns_vi_cmd")
            finally:
                pycom.ioloop().stop()

        pycom.ioloop().add_callback(_check)
        self.main(["sys", "-a", address, "-s", "/test/test_launcher3",
            "-n", "test_ns_vi_cmd"])

    def testUnknownModule(self):
        address = self.genAddress()

        with replacer(sys, "stderr", StringIO()):
            self.assertRaises(SystemExit, self.main,
                ["banana!", "-a", address, "-s", "/test/test_launcher4"])
