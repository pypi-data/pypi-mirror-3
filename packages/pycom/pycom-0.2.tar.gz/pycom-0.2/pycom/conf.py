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

"""Configuration management for clients, services and nameserver."""

import atexit
import json
import shutil
import tempfile

#: Read-only dictionary with current configuration
configuration = {}


def configure(*args, **kwargs):
    """Safe way to alter configuration.

    The only position argument should be a JSON file.
    Keyword arguments are added to global configuration.

    Example::

        import pycom
        pycom.configure(nameserver="tcp://127.0.0.1:2012")

    """
    if len(args) > 0:
        assert len(args) == 1
        _load(args[0])

    configuration.update(kwargs)


def runtime_directory():
    """Get a directory containing runtime files (e.g. IPC)."""
    global _runtime_directory

    if _runtime_directory is None:
        _runtime_directory = tempfile.mkdtemp()

    return _runtime_directory

# Private

_runtime_directory = None


@atexit.register
def _clean_runtime_directory():  # pragma: no cover
    """Empty runtime directory on exit."""
    if _runtime_directory is not None:
        shutil.rmtree(_runtime_directory)


def _load(file_name):
    """Load configuration from JSON file."""
    with open(file_name, "rt") as conf_file:
        configuration.update(json.load(conf_file))
