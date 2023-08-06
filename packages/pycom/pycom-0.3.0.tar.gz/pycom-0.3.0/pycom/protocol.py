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

"""JSON protocol details."""

import json

from six import string_types
import zmq

from . import base, constants, exceptions


def request_to_wire(iface_name, method_name, args, session_id=None):
    """Pack request to wire format."""
    return json.dumps({
        "version": constants.PROTO_VERSION,
        "interface": iface_name,
        "method": method_name,
        "session_id": session_id,
        "args": args
    }).encode("utf-8")


def request_from_wire(message):
    """Unpack request from wire format, return Request object."""
    message = json.loads(message.decode("utf-8"))

    try:
        session = _session_factory.get(message["session_id"])
    except KeyError:
        session = _session_factory.new()

    try:
        return base.Request(message["interface"], message["method"], session,
            message.get("args", None))
    except KeyError as err:
        raise exceptions.BadRequest("Field %s is required" % err.args[0])


def response_to_wire(code, error, result, session_id=None):
    """Pack result to wire format."""
    if code:
        message = {"code": code, "error": error}
    else:
        message = {"code": 0, "result": result}

    message["session_id"] = session_id

    return json.dumps(message).encode("utf-8")


def response_from_wire(message):
    """Unpack result from wire format, raise appropriate exception."""
    message = json.loads(message.decode("utf-8"))
    result_code = message["code"]
    if result_code != 0:
        raise exceptions.RemoteError(message.get("error", None) or
            "Remote error #%d" % result_code, code=result_code)

    return message.get("result", None), message.get("session_id", None)


def send_request(socket, iface, method, args, timeout=None, session_id=None):
    """Send request over 0MQ network and return result."""
    message = request_to_wire(iface, method, args, session_id=session_id)
    timeout = timeout or constants.PROTO_DEFAULT_TIMEOUT

    # Here and below we use poll() as it supports timeout
    if not socket.poll(timeout=timeout, flags=zmq.POLLOUT):
        # Timeout - assume peer is disconnected
        raise exceptions.ServiceNotAvailable("Service with interface '%s' "
            "is no longer available" % iface)

    try:
        socket.send_multipart([constants.PROTO_CMD_CALL, message],
            flags=zmq.NOBLOCK)
    except zmq.ZMQError as err:
        if err.errno == zmq.EAGAIN:
            raise exceptions.ServiceNotAvailable(
                "Service with interface '%s' is no longer available"
                    % iface)
        else:
            raise

    if not socket.poll(timeout=timeout):
        raise exceptions.ServiceNotAvailable("Service with interface '%s' "
            "is no longer available" % iface)

    try:
        status, message = socket.recv_multipart(flags=zmq.NOBLOCK)
    except zmq.ZMQError as err:
        if err.errno == zmq.EAGAIN:
            raise exceptions.ServiceNotAvailable(
                "Service with interface '%s' is no longer available"
                    % iface)
        else:
            raise

    if status != constants.PROTO_STATUS_SUCCESS:
        # Global protocol failure - world is going to explode!
        # This DOESN'T handle normal server-side exceptions
        raise exceptions.ServiceNotAvailable("Service with interface '%s' "
            "is failing" % iface)

    try:
        return response_from_wire(message)
    except exceptions.RemoteError as err:
        if err.code == constants.ERROR_METHOD_NOT_FOUND:
            raise exceptions.MethodNotFound("Method '%s' not found in "
                "interface %s" % (method, iface))
        else:
            raise


class RemoteComponent(base.BaseComponent):
    """Component working over 0MQ network."""

    def __init__(self, socket, iface):
        """C-tor. Takes 0MQ socket or address and interface name."""
        super(RemoteComponent, self).__init__()
        if isinstance(socket, string_types):
            self.socket = context.socket(zmq.REQ)
            self.socket.connect(socket)
        else:
            self.socket = socket

        self.iface = iface
        self.session_id = None

    def invoke(self, method_name, args=None,
            timeout=None):
        """Invoke given method with args
        (see :meth:`pycom.BaseComponent.invoke` for details)."""
        result, session_id = send_request(self.socket, self.iface, method_name,
             args, timeout=timeout, session_id=self.session_id)
        if session_id is not None:
            self.session_id = session_id
        return result


context = zmq.Context()  #: Shared 0MQ context

# Private

_session_factory = base.SessionFactory()
