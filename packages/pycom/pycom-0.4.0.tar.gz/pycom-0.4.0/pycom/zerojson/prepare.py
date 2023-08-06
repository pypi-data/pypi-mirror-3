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

"""PREPARE command implementation.

This is the draft implementation of ``PREPARE`` command. Do not use it yet!

"""

from .. import base, constants, exceptions, interfaces, utils

from . import common


class PrepareCommand(common.BaseCommand):
    """PREPARE command implementation.

    Inherits :class:`pycom.zerojson.common.BaseCommand`.

    """

    def __init__(self):
        """Constructor."""
        super(PrepareCommand, self).__init__()

    # pylint: disable-msg=W0221

    def request_to_dict(self, iface_name, method_name, args, session_id=None):
        """Dump request to Python dict."""
        return {
            "interface": iface_name,
            "method": method_name,
            "session_id": session_id,
            "args": args
        }

    def response_to_dict(self, code, error, result, session_id=None):
        """Dump response to Python dict."""
        if code:
            return {
                "session_id": session_id
            }
        else:
            assert not error
            return {
                "result": result,
                "session_id": session_id
            }

    def request_from_dict(self, data):
        """Get request from Python dict."""
        try:
            session = self.session_factory.get(data["session_id"])
        except KeyError:
            session = self.session_factory.new()

        try:
            return base.Request(data["interface"], data["method"], session,
                data.get("args", None))
        except KeyError as err:
            raise exceptions.BadRequest("Field %s is required" % err.args[0])

    def response_from_dict(self, data):
        """Get request from Python dict."""
        return data.get("result", None), data.get("session_id", None)

    # pylint: enable-msg=W0221
