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

"""Tests for pycom.zerojson.sessions."""

import datetime

import pycom
from pycom import base, constants, utils
from pycom.zerojson import eventloop

from .utils import unittest, Replacer


class TestExpiringFactory(unittest.TestCase):

    timeout = 3

    def testExpire(self):
        factory = eventloop.ExpiringFactory(base.Session, timeout=1)  # 1ms
        session = factory.new()

        def _check():
            try:
                self.assertRaises(KeyError, factory.get, session.session_id)
            finally:
                eventloop.ioloop().stop()

        eventloop.ioloop().add_timeout(
            datetime.timedelta(milliseconds=10), _check)
        eventloop.ioloop().start()

    def testRescheduleAndDrop(self):
        factory = eventloop.ExpiringFactory(base.Session, timeout=200)  # 1ms
        session = factory.new()

        def _check1():
            factory.get(session.session_id)

        def _check2():
            try:
                factory.get(session.session_id)
                factory.drop(session.session_id)
                self.assertRaises(KeyError, factory.get, session.session_id)
            finally:
                eventloop.ioloop().add_callback(eventloop.ioloop().stop)

        eventloop.ioloop().add_timeout(
            datetime.timedelta(milliseconds=150), _check1)
        eventloop.ioloop().add_timeout(
            datetime.timedelta(milliseconds=300), _check2)
        eventloop.ioloop().start()
