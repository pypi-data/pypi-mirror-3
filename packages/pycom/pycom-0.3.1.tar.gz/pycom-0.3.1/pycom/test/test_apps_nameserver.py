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

import pycom
from pycom import constants, exceptions, protocol
from pycom.apps import nameserver

from .utils import unittest

class TestNameServer(unittest.TestCase):

    def setUp(self):
        self.component = nameserver.NameServer.__interface__
        self.service = self.component.instance
        self.service._services = {}
        self.service._registry = {}

    def testStat(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_STAT), {})

    def testRegisterOk(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interface": "test_apps_nameserver.testRegisterOk",
                "service": "/test_apps_nameserver/testRegisterOk",
                "address": "null://null"
            }), {})
        item = self.service._services["/test_apps_nameserver/testRegisterOk"]
        self.assertEqual(item.interface, "test_apps_nameserver.testRegisterOk")
        self.assertEqual(item.service, "/test_apps_nameserver/testRegisterOk")
        self.assertEqual(item.address, "null://null")
        self.assertEqual(
            len(self.service._registry["test_apps_nameserver.testRegisterOk"]),
            1)

    def testInterfaceReregisterOk(self):
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interface": "test_apps_nameserver.testReregisterOk",
                "service": "/test_apps_nameserver/testReregisterOk",
                "address": "null://null"
            }), {})
        self.assertEqual(self.component.invoke(constants.NS_METHOD_REGISTER,
            args={
                "interface": "test_apps_nameserver.testReregisterOk",
                "service": "/test_apps_nameserver/testReregisterOk2",
                "address": "null://null"
            }), {})
        item = self.service._services["/test_apps_nameserver/testReregisterOk"]
        self.assertEqual(item.interface, "test_apps_nameserver.testReregisterOk")
        self.assertEqual(item.service, "/test_apps_nameserver/testReregisterOk")
        self.assertEqual(item.address, "null://null")
        self.assertEqual(
            len(self.service._registry["test_apps_nameserver.testReregisterOk"]),
            2)

    def testRegisterNone(self):
        self.assertRaises(exceptions.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER)

    def testRegisterWOAddress(self):
        self.assertRaises(exceptions.BadRequest, self.component.invoke,
            constants.NS_METHOD_REGISTER,
            args={
                "interface": "test_apps_nameserver.testRegisterWOAddress",
                "service": "/test_apps_nameserver/testRegisterWOAddress",
            })

    def testLocateOk(self):
        self.service._registry["test_apps_nameserver.testLocateOk"] = [
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateOk",
                "/test_apps_nameserver/testLocateOk")
        ]
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testLocateOk"
            }), {
                "service": "/test_apps_nameserver/testLocateOk",
                "address": "null://null"
            })

    def testLocateNone(self):
        self.assertRaises(exceptions.BadRequest, self.component.invoke,
            constants.NS_METHOD_LOCATE)

    def testLocateList(self):
        self.service._registry["test_apps_nameserver.testLocateList"] = [
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateList",
                "/test_apps_nameserver/testLocateList"),
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateList",
                "/test_apps_nameserver/testLocateList2")
        ]
        self.assertListEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testLocateList",
                "as_list": True
            }), [
                {
                    "service": "/test_apps_nameserver/testLocateList",
                    "address": "null://null"
                },
                {
                    "service": "/test_apps_nameserver/testLocateList2",
                    "address": "null://null"
                }
            ])

    def testLocateEmpty(self):
        self.service._registry["test_apps_nameserver.testLocateEmpty"] = [
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateEmpty",
                "/test_apps_nameserver/testLocateEmpty")
        ]
        self.assertRaises(exceptions.BadRequest, self.component.invoke,
            constants.NS_METHOD_LOCATE,
            args={})

    def testLocateWithService(self):
        self.service._registry["test_apps_nameserver.testLocateWithService"] = [
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateWithService",
                "/test_apps_nameserver/testLocateWithService"),
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateWithService",
                "/test_apps_nameserver/testLocateWithService2"),
            nameserver._Record("null://null",
                "test_apps_nameserver.testLocateWithService",
                "/test_apps_nameserver/testLocateWithService3")
        ]
        self.assertDictEqual(self.component.invoke(constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testLocateWithService",
                "service": "/test_apps_nameserver/testLocateWithService2",
            }), {
                "service": "/test_apps_nameserver/testLocateWithService2",
                "address": "null://null"
            })

    def testLocateMissing(self):
        self.assertRaises(exceptions.ServiceNotFound, self.component.invoke,
            constants.NS_METHOD_LOCATE,
            args={
                "interface": "test_apps_nameserver.testLocateMissing"
            })

    def testListServices(self):
        self.service._services["/test_apps_nameserver/testListServices"] = \
            nameserver._Record("null://null",
                "test_apps_nameserver.testListServices",
                "/test_apps_nameserver/testListServices")
        self.assertListEqual(self.component.invoke(
            constants.NS_METHOD_LIST_SERVICES,), [{
                "service": "/test_apps_nameserver/testListServices",
                "interface": "test_apps_nameserver.testListServices"
            }])
