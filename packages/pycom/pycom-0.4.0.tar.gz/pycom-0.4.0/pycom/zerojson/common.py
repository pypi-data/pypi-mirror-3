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

"""Base class for commands."""

import json

import zmq

from .. import base, constants, exceptions


class BaseCommand(object):
    """Base implementation for any command.

    Typical request-response processing chain looks like::

        <client>
         request_to_wire (request_to_dict => dict_to_wire) ==>
        <server>
         ==> request_from_wire (dict_from_wire => request_from_dict) ==>
         ==> process_request [request processing goes here] ==>
         ==> response_to_wire (response_to_dict => dict_to_wire) ==>
        <client>
         ==> response_from_wire (dict_from_wire => response_from_dict)

    """

    session_factory = base.UUIDFactory(base.Session)  #: Shared session factory

    call_factory = base.UUIDFactory(base.Call)  #: Shared factory for call info

    def request_to_wire(self, *args, **kw):
        """Pack request to wire format."""
        return dict_to_wire(self.request_to_dict(*args, **kw))

    def response_to_wire(self, code, error, *args, **kw):
        """Pack result to wire format."""
        if code:
            message = {"code": code, "error": error}
        else:
            message = {"code": 0}

        message.update(self.response_to_dict(code, error, *args, **kw))
        return dict_to_wire(message, with_version=False)

    def request_from_wire(self, message):
        """Unpack request from wire format."""
        return self.request_from_dict(dict_from_wire(message))

    def response_from_wire(self, message):
        """Unpack request from wire format."""
        message = dict_from_wire(message)
        result_code = message["code"]
        if result_code != 0:
            raise exceptions.RemoteError(message.get("error", None) or
                "Remote error #%d" % result_code, code=result_code)

        return self.response_from_dict(message)

    # Protected

    # pylint: disable-msg=W0613,R0201

    def request_to_dict(self, *args, **kw):
        """Dump request to Python dict."""
        raise NotImplementedError()  # pragma: no cover

    def response_to_dict(self, *args, **kw):
        """Dump response to Python dict.

        Base version just returns empty dict.

        """
        return {}

    def request_from_dict(self, *args, **kw):
        """Get request from Python dict."""
        raise NotImplementedError()  # pragma: no cover

    def response_from_dict(self, *args, **kw):
        """Get request from Python dict."""
        raise NotImplementedError()  # pragma: no cover

    def real_process_request(self, request, *other_parts):
        """Call to process request."""
        raise NotImplementedError()  # pragma: no cover

    # pylint: enable-msg=W0613,R0201

    def process_request(self, json_body, *other_parts):
        """Call to process request.

        Override `real_process_request` to change behaviour.

        """
        try:
            request = self.request_from_wire(json_body)
        except exceptions.BadRequest as err:
            result_parts = (err.code, str(err), None)
        else:
            result_parts = self.real_process_request(request, *other_parts)

        return self.response_to_wire(*result_parts)


def dict_to_wire(data, with_version=True):
    """Pack Python dictionary *data* into wire format."""
    if with_version:
        data["version"] = constants.PROTO_VERSION
    return json.dumps(data).encode("utf-8")


def dict_from_wire(data):
    """Unpack Python dictionary from wire format *data*.

    Raise BadRequest on errors.

    """
    try:
        return json.loads(data.decode("utf-8"))
    except UnicodeError:
        raise exceptions.BadRequest("Invalid encoding, expected UTF-8")
    except ValueError as err:
        raise exceptions.BadRequest("Cannot decode response: " + str(err))


context = zmq.Context()  #: Shared 0MQ context
