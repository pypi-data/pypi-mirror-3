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
from pycom.ext import checks

from .test_interfaces import BaseTest
from zerojson.testing import unittest


class TestCheckArgument(BaseTest, unittest.TestCase):

    def testTypeChecks(self):
        iface = "test.test_ext.TestCheckArgument.testTypeChecks"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @checks.check_argument("arg1", valid_types=str)
            @checks.check_argument("arg2", valid_types=(int, type(None)))
            @pycom.method(meth)
            def meth1(self, request, arg1, arg2=42): pass  # pragma: no cover

        component = SimpleInterface.__interface__
        component.invoke(meth, {"arg1": "", "arg2": 2})
        component.invoke(meth, {"arg1": "", "arg2": None})
        component.invoke(meth, {"arg1": ""})

        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_ext.TestCheckArgument.testTypeChecks.method1",
            component.invoke, meth,
            {"arg1": 42, "arg2": None})
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_ext.TestCheckArgument.testTypeChecks.method1",
            component.invoke, meth,
            {"arg1": 42})
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_ext.TestCheckArgument.testTypeChecks.method1",
            component.invoke, meth,
            {"arg1": "", "arg2": ""})

    def testMessage(self):
        iface = "test.test_ext.TestCheckArgument.testMessage"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @checks.check_argument("arg1", valid_types=str,
                error_message="MESSAGE")
            @pycom.method(meth)
            def meth1(self, request, arg1): pass  # pragma: no cover

        component = SimpleInterface.__interface__
        self.assertRaisesRegexp(pycom.BadRequest, "MESSAGE", component.invoke,
            meth, {"arg1": 42})

    def testValidator(self):
        iface = "test.test_ext.TestCheckArgument.testTypeChecks"
        meth = "method1"

        @pycom.interface(iface)
        class SimpleInterface(object):

            @checks.check_argument("arg1", valid_types=str,
                validator=lambda name, value: len(value) > 0)
            @checks.check_argument("arg2",
                validator=lambda name, value: value is not None)
            @pycom.method(meth)
            def meth1(self, request, arg1, arg2=42): pass  # pragma: no cover

        component = SimpleInterface.__interface__
        component.invoke(meth, {"arg1": "str", "arg2": 2})
        component.invoke(meth, {"arg1": "str"})

        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_ext.TestCheckArgument.testTypeChecks.method1",
            component.invoke, meth,
            {"arg1": "str", "arg2": None})
        self.assertRaisesRegexp(pycom.BadRequest,
            "test.test_ext.TestCheckArgument.testTypeChecks.method1",
            component.invoke, meth,
            {"arg1": "", "arg2": 2})
