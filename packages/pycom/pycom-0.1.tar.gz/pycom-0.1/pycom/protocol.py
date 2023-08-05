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

import collections
import json

import zmq

from . import constants, exceptions


class Request(collections.namedtuple("Request", "interface method args")):
    """Named tuple representing request."""


def request_to_wire(iface_name, method_name, args):
    """Pack request to wire format."""
    return json.dumps({
        "version": constants.PROTO_VERSION,
        "interface": iface_name,
        "method": method_name,
        "args": args
    }).encode("utf-8")


def request_from_wire(message):
    """Unpack request from wire format, return Request object."""
    message = json.loads(message.decode("utf-8"))
    try:
        return Request(message["interface"], message["method"],
            message.get("args", None))
    except KeyError as err:
        raise exceptions.BadRequest("Field %s is required" % err.args[0])


def response_to_wire(code, error, result):
    """Pack result to wire format."""
    if code:
        message = {"code": code, "error": error}
    else:
        message = {"code": 0, "result": result}

    return json.dumps(message).encode("utf-8")


def response_from_wire(message):
    """Unpack result from wire format, raise appropriate exception."""
    message = json.loads(message.decode("utf-8"))
    result_code = message["code"]
    if result_code != 0:
        raise exceptions.RemoteError(message.get("error", None) or
            "Remote error #%d" % result_code, code=result_code)

    return message.get("result", None)


def send_request(socket, iface, method, args, timeout=None):
    """Send request over 0MQ network and return result."""
    message = request_to_wire(iface, method, args)
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
            raise exceptions.MethodNotFound("Method %s not found for "
                "interface %s" % (method, iface))
        else:
            raise


context = zmq.Context()  #: Shared 0MQ context
