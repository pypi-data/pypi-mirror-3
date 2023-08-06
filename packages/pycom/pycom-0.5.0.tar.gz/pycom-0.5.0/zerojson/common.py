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

from . import async, constants, eventloop, exceptions


class Request(object):
    """Request object.

    .. attribute:: interface

       Current interface name

    .. attribute:: method

       Current method name

    .. attribute:: session

       Session for current component - dict-like object of
       type :class:`pycom.zerojson.Session`

    .. attribute:: args

       Arguments passed by client side as Python object

    .. attribute:: extensions

       Dictionary with extensions data

    """

    def __init__(self, interface, method, session=None, args=None,
            extensions=None):
        """Initializer."""
        self.interface = interface
        self.method = method
        self.session = session if session is not None else Session(None)
        self.args = args
        self.extensions = extensions or {}

    def response(self, result):
        """Build response object to return from method.

        *result* is a JSON-serializable entity to return to client.

        Returns :class:`pycom.zerojson.Response` object.

        """
        return Response(self, result=result)

    def error(self, code, message=None):
        """Build response object with error."""
        return Response(self, code=code, message=message)


class Response(object):
    """Response object.

    .. attribute:: request

       :class:`zerojson.Request` object that issued this response

    .. attribute:: result

       Call result as Python object

    """

    def __init__(self, request, result=None, code=0, message=None,
            session_id=None, extensions=None):
        """Initializer."""
        self.request = request
        self.result = result
        self.code = code
        self.message = message
        self.session_id = session_id or (
            request and request.session.session_id)
        self.extensions = extensions or {}


class Session(dict):
    """Class representing session.

    Inherits from `dict`, provides one additional attribute:

    .. attribute: session_id

       UUID of session

    """

    __slots__ = ("_owner", "session_id")

    def __init__(self, session_id, *args, **kw):
        """Constructor."""
        self._owner = kw.pop("session_factory", None)
        super(Session, self).__init__(*args, **kw)
        self.session_id = session_id

    def discard(self):
        """Discard this sessions and all it's data."""
        if self._owner is not None:
            self._owner.drop(self.session_id)
        self.clear()


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

    session_factory = eventloop.ExpiringFactory(Session,
        timeout=constants.PROTO_SESSION_TIMEOUT,
        message="Session '%s' expired")  #: Session factory

    # call_factory = utils.UUIDFactory(Call)  #: Shared factory for call info

    def __init__(self, server=None):
        """Constructor."""
        self.server = server

    def request_to_wire(self, request, **kw):
        """Pack request to wire format."""
        return dict_to_wire(self.request_to_dict(request, **kw))

    def response_to_wire(self, response, **kw):
        """Pack result to wire format."""
        if response.code:
            message = {"code": response.code, "error": response.message}
        else:
            message = {"code": 0}

        message.update(self.response_to_dict(response, **kw))
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

    def response_to_dict(self, response):
        """Dump response to Python dict.

        Base version just returns empty dict.

        """
        return {}

    def request_from_dict(self, data):
        """Get request from Python dict."""
        raise NotImplementedError()  # pragma: no cover

    def response_from_dict(self, data):
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
        assert self.server is not None

        try:
            request = self.request_from_wire(json_body)
        except exceptions.RemoteError as err:
            response = Response(None, code=err.code, message=str(err))
        else:
            response = self.real_process_request(request, *other_parts)

        if isinstance(response, async.Future):
            response.add_callback(self.response_to_wire)
            return response

        return self.response_to_wire(response)


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
