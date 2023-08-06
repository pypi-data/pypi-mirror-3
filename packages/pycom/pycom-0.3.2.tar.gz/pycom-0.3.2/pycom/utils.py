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

"""Auxiliary utils."""

import logging
import os
import sys

from . import __file__ as pycom_file


def logger():
    """Returns current logger for PyCOM."""
    return logging.getLogger("pycom")


def find_conf_file(basename):
    """Finds configuration file with name `basename`."""
    conf_file = os.path.join(sys.prefix, "share", "pycom", basename)

    if not os.path.exists(conf_file):
        # EasyInstall sandboxing workaround
        conf_file = os.path.join(os.path.dirname(pycom_file), "..",
            "share", "pycom", "ns.conf")

    if os.path.exists(conf_file):
        return conf_file
    else:
        return None

# Initialize logger

_logging_formatter = logging.Formatter(
    fmt="PyCOM %(levelname)s %(asctime)s: %(message)s")
_logging_handler = logging.StreamHandler()
_logging_handler.setFormatter(_logging_formatter)
logger().addHandler(_logging_handler)
