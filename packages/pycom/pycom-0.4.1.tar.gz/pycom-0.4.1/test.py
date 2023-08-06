#!/usr/bin/env python
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

"""Tests runner."""

from __future__ import print_function

import logging
import os

if __name__ == '__main__':
    try:
        import coverage
    except ImportError:
        print("WARNING: Coverage.py is unavailable")
        print("         download from http://nedbatchelder.com/code/coverage")
        coverage = None

    if coverage is not None:
        coverage = coverage.coverage(branch=True,
            include="*/pycom/*", omit=["test.py", "pycom/test/utils.py"])
        coverage.erase()
        coverage.start()

    from pycom import utils

    utils.logger().removeHandler(utils._logging_handler)
    new_handler = logging.StreamHandler(open("test.log", "wt"))
    new_handler.setFormatter(utils._logging_formatter)
    utils.logger().addHandler(new_handler)
    utils.logger().setLevel(logging.DEBUG)

    # Prevent pycom.main() from overwriting logging level
    os.environ["PYCOM_LOGGING_LEVEL"] = str(logging.DEBUG)

    from pycom.test.utils import unittest

    tests = unittest.defaultTestLoader.discover(".")
    runner = unittest.runner.TextTestRunner()
    runner.run(tests)

    if coverage is not None:
        coverage.stop()
        coverage.report(include="*/pycom/*",
            ignore_errors=False, show_missing=True)
