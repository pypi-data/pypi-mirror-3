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

"""Tests for pycom.utils and pycom.base."""

import os
import sys

import pycom
from pycom import base, utils

from .utils import unittest, Replacer

class TestFindConf(unittest.TestCase):

    def testMissing(self):
        self.assertEqual(utils.find_conf_file("banana!"), None)

    def testExisting(self):
        expected = os.path.join(sys.prefix, "share", "pycom", "test1.cfg")
        def _fake_exists(path):
            return path == expected

        with Replacer(os.path, "exists", _fake_exists):
            self.assertEqual(utils.find_conf_file("test1.cfg"), expected)


class TestUUIDFactory(unittest.TestCase):

    def testExisting(self):
        factory = utils.UUIDFactory(base.Session)
        sessid = factory.new().session_id
        self.assertTrue(sessid)

        self.assertDictEqual(factory.get(sessid), {})
        self.assertIsInstance(factory.get(sessid), base.Session)
        self.assertEqual(factory.get(sessid).session_id, sessid)
        self.assertIs(factory.get(sessid), factory.get(sessid))

        factory.get(sessid)["item"] = 42

        self.assertDictEqual(factory.get(sessid), {"item": 42})

        factory.get(sessid).discard()
        self.assertRaises(KeyError, factory.get, sessid)

    def testNonExisting(self):
        factory = utils.UUIDFactory(base.Session)
        self.assertRaises(KeyError, factory.get, "banana!")

    def testDiscardWoOwner(self):
        base.Session(None).discard()
