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

"""Tests for pycom.apps.nameserver."""

import datetime

import six

import pycom
from pycom import constants
from pycom.apps import nameserver

from zerojson.testing import unittest, replacer
from zerojson.testing import OrderedDict, OrderedDictWithSet

class BaseTest(object):

    def setUp(self):
        self.component = nameserver.NameServer.__interface__
        self.service = self.component.instance
        self.service._services = OrderedDict()
        self.service._registry = OrderedDictWithSet()


class TestCommon(BaseTest, unittest.TestCase):

    def testStat(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_STAT), {})

    def testNoAuth(self):
        old_auth = pycom.configuration.get("authentication", {})
        pycom.configure(authentication=dict(policy="required"))
        try:
            self.component.invoke(constants.NS_METHOD_STAT)
        finally:
            pycom.configuration["authentication"] = old_auth


class TestRegister(BaseTest, unittest.TestCase):

    def testRegisterOk(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testRegisterOk"],
                "service": "/test_apps_nameserver/testRegisterOk",
                "address": "null://null"
            }), {})
        item = self.service._services["/test_apps_nameserver/testRegisterOk"]
        self.assertEqual(item.interfaces, ["test_apps_nameserver.testRegisterOk"])
        self.assertEqual(item.service, "/test_apps_nameserver/testRegisterOk")
        self.assertEqual(item.address, "null://null")

        self.assertEqual(
            self.service._registry["test_apps_nameserver.testRegisterOk"],
            set(["/test_apps_nameserver/testRegisterOk"]))

    def testRegisterOkUnicode(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": [six.u("test_apps_nameserver.testRegisterOk")],
                "service": six.u("/test_apps_nameserver/testRegisterOk"),
                "address": six.u("null://null")
            }), {})
        item = self.service._services["/test_apps_nameserver/testRegisterOk"]
        self.assertEqual(item.interfaces, ["test_apps_nameserver.testRegisterOk"])
        self.assertEqual(item.service, "/test_apps_nameserver/testRegisterOk")
        self.assertEqual(item.address, "null://null")

        self.assertEqual(
            self.service._registry["test_apps_nameserver.testRegisterOk"],
            set(["/test_apps_nameserver/testRegisterOk"]))

    def testInterfaceReregisterOk(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk"],
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null"
            }), {})
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk"],
                "service": "/test_apps_nameserver/testReregisterOk2",
                "address": "null://null"
            }), {})
        item = self.service._services["/test_apps_nameserver/testReregisterOk"]
        self.assertEqual(item.interfaces, ["test_apps_nameserver.testReregisterOk"])
        self.assertEqual(item.service, "/test_apps_nameserver/testReregisterOk")
        self.assertEqual(item.address, "null://null")
        self.assertIn("test_apps_nameserver.testReregisterOk",
            self.service._registry)
        self.assertEqual(
            self.service._registry["test_apps_nameserver.testReregisterOk"],
            set([
                "/test_apps_nameserver/testReregisterOk",
                "/test_apps_nameserver/testReregisterOk2"
            ]))

    def testServiceReregisterFailure(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk"],
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null"
            }), {})
        self.assertRaises(pycom.AccessDenied, self.component.invoke,
            constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk2"],
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null2"
            })
        return

    def testServiceReregisterOk(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk"],
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null"
            }), {})
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testReregisterOk2"],
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null"
            }), {})
        item = self.service._services["/test_apps_nameserver/testReregisterOk"]
        self.assertEqual(item.interfaces, ["test_apps_nameserver.testReregisterOk2"])
        self.assertEqual(item.service, "/test_apps_nameserver/testReregisterOk")
        self.assertEqual(item.address, "null://null")
        self.assertEqual(
            self.service._registry["test_apps_nameserver.testReregisterOk2"],
            set([
                "/test_apps_nameserver/testReregisterOk"
            ]))
        self.assertEqual(self.service._registry["test_apps_nameserver.testReregisterOk"],
            set())

    def testRegisterNone(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER)

    def testRegisterWOAddress(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["test_apps_nameserver.testRegisterWOAddress"],
                "service": "/test_apps_nameserver/testRegisterWOAddress",
            })

    def testRegisterWrongList(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER,
            args={
                "interfaces": 42,
                "service": "/test_apps_nameserver/testRegisterWrongList",
                "address": "null://null"
            })

    def testRegisterWrongItem(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER,
            args={
                "interfaces": ["s", 42],
                "service": "/test_apps_nameserver/testRegisterWrongItem",
                "address": "null://null"
            })


class TestTimeout(BaseTest, unittest.TestCase):

    timeout = 3

    def testExpire(self):
        def _check():
            try:
                self.assertNotIn("test_apps_nameserver.testExpire",
                    self.service._registry)
                self.assertNotIn("/test_apps_nameserver/testExpire",
                    self.service._services)
            finally:
                pycom.ioloop().stop()

        pycom.ioloop().add_timeout(datetime.timedelta(milliseconds=100),
            _check)

        with replacer(constants, "NS_SERVICE_TIMEOUT", 10):
            self.component.invoke(constants.NS_METHOD_REGISTER,
                args={
                    "interfaces": ["test_apps_nameserver.testExpire"],
                    "service": "/test_apps_nameserver/testExpire",
                    "address": "null://null"
                })
            pycom.ioloop().start()


class TestWithData(BaseTest):

    maxDiff = None

    def setUp(self):
        super(TestWithData, self).setUp()

        self.service._services["/test_apps_nameserver/testIface"] = nameserver._Record(
            address="null://null",
            interfaces=set(["test_apps_nameserver.testIface",
                "test_apps_nameserver.testIface0"]),
            service="/test_apps_nameserver/testIface"
        )
        self.service._services["/test_apps_nameserver/testIface2"] = nameserver._Record(
            address="null://null",
            interfaces=set(["test_apps_nameserver.testIface"]),
            service="/test_apps_nameserver/testIface2"
        )
        self.service._services["/test_apps_nameserver/testIface3"] = nameserver._Record(
            address="null://null",
            interfaces=set(["test_apps_nameserver.testIface0", "test_apps_nameserver.testIface#"]),
            service="/test_apps_nameserver/testIface3"
        )
        self.service._services["/test_apps_nameserver/testIface4"] = nameserver._Record(
            address="null://null",
            interfaces=set(["test_apps_nameserver.testIface"]),
            service="/test_apps_nameserver/testIface4"
        )
        self.service._registry["test_apps_nameserver.testIface"] = set([
            "/test_apps_nameserver/testIface",
            "/test_apps_nameserver/testIface2",
            "/test_apps_nameserver/testIface4"
        ])
        self.service._registry["test_apps_nameserver.testIface0"] = set([
            "/test_apps_nameserver/testIface",
            "/test_apps_nameserver/testIface3"
        ])
        self.service._registry["test_apps_nameserver.testIface#"] = set([
            "/test_apps_nameserver/testIface3"
        ])


class TestLocate(TestWithData, unittest.TestCase):

    def testLocateSingle(self):
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testIface#"
            }), {
                "service": "/test_apps_nameserver/testIface3",
                "address": "null://null",
                "interfaces": ["test_apps_nameserver.testIface0", "test_apps_nameserver.testIface#"]
            })

    def testLocateUnicode(self):
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": six.u("test_apps_nameserver.testIface#")
            }), {
                "service": "/test_apps_nameserver/testIface3",
                "address": "null://null",
                "interfaces": ["test_apps_nameserver.testIface0", "test_apps_nameserver.testIface#"]
            })

    def testLocateNone(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_LOCATE)

    def testLocateEmpty(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_LOCATE,
            args={})

    def testLocateWithService(self):
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testIface",
                "service": "/test_apps_nameserver/testIface2",
            }), {
                "service": "/test_apps_nameserver/testIface2",
                "address": "null://null",
                "interfaces": ["test_apps_nameserver.testIface"]
            })

    def testLocateWithServiceUnicode(self):
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testIface",
                "service": six.u("/test_apps_nameserver/testIface2"),
            }), {
                "service": "/test_apps_nameserver/testIface2",
                "address": "null://null",
                "interfaces": ["test_apps_nameserver.testIface"]
            })

    def testLocateMissing(self):
        self.assertRaises(pycom.ServiceNotFound, self.component.invoke,
            constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testLocateMissing"
            })


class TestListServices(TestWithData, unittest.TestCase):

    ALL = [
        {
            "service": "/test_apps_nameserver/testIface",
            "address": "null://null",
            "interfaces": ["test_apps_nameserver.testIface0",
                "test_apps_nameserver.testIface"]
        },
        {
            "service": "/test_apps_nameserver/testIface2",
            "address": "null://null",
            "interfaces": ["test_apps_nameserver.testIface"]
        },
        {
            "service": "/test_apps_nameserver/testIface3",
            "address": "null://null",
            "interfaces": ["test_apps_nameserver.testIface0",
                "test_apps_nameserver.testIface#"]
        },
        {
            "service": "/test_apps_nameserver/testIface4",
            "address": "null://null",
            "interfaces": ["test_apps_nameserver.testIface"]
        }
    ]

    def testListAllServices(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES),
            self.ALL)


    def testListServicesWithInterface(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "interface": "test_apps_nameserver.testIface"
            }), self.ALL)

    def testListServicesWithInterfaceRe(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "interface": r"test_apps_nameserver\.testIface$"
            }), [
                {
                    "service": "/test_apps_nameserver/testIface",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface0",
                        "test_apps_nameserver.testIface"]
                },
                {
                    "service": "/test_apps_nameserver/testIface2",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface"]
                },
                {
                    "service": "/test_apps_nameserver/testIface4",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface"]
                }
            ])

    def testListServicesWithInterfaceRe2(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "interface": r".*nameserver\.testIface$"
            }), [
                {
                    "service": "/test_apps_nameserver/testIface",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface0",
                        "test_apps_nameserver.testIface"]
                },
                {
                    "service": "/test_apps_nameserver/testIface2",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface"]
                },
                {
                    "service": "/test_apps_nameserver/testIface4",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface"]
                }
            ])

    def testListServicesWithInterfaceRe3(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "interface": r"nameserver\.testIface$"
            }), [])

    def testListServicesWithInterfaceUnicode(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "interface": six.u("test_apps_nameserver.testIface")
            }),
            self.ALL)

    def testListServicesWithWrongInterface(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_LIST_SERVICES, args={
                "interface": "((nameserver\.testIface$"
            })

    def testListServicesWithService(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "service": "/test_apps_nameserver/testIface"
            }), self.ALL)

    def testListServicesWithServiceUnicode(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "service": six.u("/test_apps_nameserver/testIface")
            }), self.ALL)

    def testListServicesWithServiceRe(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "service": "/test_apps_nameserver/testIface$"
            }), [
                {
                    "service": "/test_apps_nameserver/testIface",
                    "address": "null://null",
                    "interfaces": ["test_apps_nameserver.testIface0",
                        "test_apps_nameserver.testIface"]
                }
            ])

    def testListServicesWithServiceRe3(self):
        self.assertListEqual(
            self.component.invoke(constants.NS_METHOD_LIST_SERVICES,
            args={
                "service": "nameserver/testIface$"
            }), [])

    def testListServicesWithWrongService(self):
        self.assertRaises(pycom.BadRequest, self.component.invoke,
            constants.NS_METHOD_LIST_SERVICES, args={
                "service": "((nameserver/testIface$"
            })
