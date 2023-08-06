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

"""Tests for zerojson.common."""

import collections
import json

import zerojson
from .. import common, constants
from ..testing import encode_utf8, unittest


class TestWireFormat(unittest.TestCase):

    def _toWireHelper(self, result, jmsg, att=None):
        self.assertEqual(json.loads(result.decode("utf-8")), jmsg)

    def testToWireVersion(self):
        self._toWireHelper(common.dict_to_wire({"1": 2}),
            {"1": 2, "version": constants.PROTO_VERSION})

    def testToWireWoVersion(self):
        self._toWireHelper(common.dict_to_wire({"1": 2}, with_version=False),
            {"1": 2})

    def testFromWireValid(self):
        self.assertEqual(common.dict_from_wire(encode_utf8('{"1": 2}')),
            {"1": 2})

    def testFromWireNotJSON(self):
        self.assertRaises(zerojson.BadRequest,common.dict_from_wire,
            encode_utf8('----'))

    def testFromWireNotUnicode(self):
        self.assertRaises(zerojson.BadRequest,common.dict_from_wire,
            b'\xff\xff')


class TestBaseProcessRequest(unittest.TestCase):

    def setUp(self):
        self.demo_data = b'"DATA!"'
        self.demo_result = ("DATA!", "DATA!")
        self.demo_parts = ("1", "2", "3")
        self.demo_response_class = collections.namedtuple("Response",
            "code message attachment")

        class DummyCommand(common.BaseCommand):

            bad_request = False
            response_code = 0
            message = None

            def request_from_dict(self2, data):
                if self2.bad_request:
                    raise zerojson.BadRequest("TestBaseProcessRequest")
                return (data, data)

            def real_process_request(self2, request, *other_parts):
                self.assertEqual(request, self.demo_result)
                self.assertEqual(other_parts, self.demo_parts)
                return self.demo_response_class(
                    self2.response_code, self2.message, None)

        self.command = DummyCommand(object)

    def testAssertionOnNoServer(self):
        self.assertRaises(AssertionError,
            self.command.__class__(None).process_request, "{}")

    def testValidRequest(self):
        result = self.command.process_request(self.demo_data, *self.demo_parts)
        self.assertEqual(json.loads(result[0].decode("utf-8")), {
            "code": 0
        })

    def testBadRequest(self):
        self.command.bad_request = True
        result = self.command.process_request(self.demo_data, *self.demo_parts)
        self.assertEqual(json.loads(result[0].decode("utf-8")), {
            "code": zerojson.constants.ERROR_BAD_REQUEST,
            "error": "TestBaseProcessRequest"
        })
