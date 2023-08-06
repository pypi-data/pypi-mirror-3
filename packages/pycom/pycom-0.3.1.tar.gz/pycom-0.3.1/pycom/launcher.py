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

"""Main routine implementation."""

import zmq
from zmq import eventloop
from six import iterkeys

from . import base, constants, exceptions, interfaces, nsclient
from . import protocol, utils


def ioloop():
    """Returns 0MQ *IOLoop* instance for current event loop.

    Roughly equivalent to::

        zmq.eventloop.IOLoop.instance()

    """
    return eventloop.IOLoop.instance()


def main():
    """Starts main loop for a service.

    Raises :exc:`pycom.ConfigurationError` if not configured properly -
    see :doc:`config` for details.

    Returns 0MQ IOLoop exit code.

    """
    try:
        address = base.configuration["address"]
    except KeyError:
        raise exceptions.ConfigurationError("Set address in the configuration")

    try:
        service = base.configuration["service"]
    except KeyError:
        raise exceptions.ConfigurationError("Set service in the configuration")

    sock = protocol.context.socket(zmq.REP)
    sock.bind(address)

    ns_component = nsclient.nameserver()
    for interface in iterkeys(interfaces.registry):
        ns_component.invoke(constants.NS_METHOD_REGISTER, args={
            "address": address,
            "interface": interface,
            "service": service
        })

    ioloop().add_handler(sock, _recv_ready, ioloop().READ)
    return ioloop().start()


# Private


def _recv_ready(sock, events):  # pylint: disable-msg=W0613
    """Some messages are ready for reading."""
    while True:
        try:
            try:
                request_parts = sock.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.ZMQError as err:
                if err.errno == zmq.EAGAIN:
                    return
                else:
                    raise  # pragma: no cover

            utils.logger().debug("REQUEST %s", request_parts)

            body = _process_call(request_parts)

            utils.logger().debug("RESPONSE %s", body)

            sock.send_multipart([constants.PROTO_STATUS_SUCCESS, body])
        except:  # pragma: no cover
            utils.logger().critical("EXCEPTION IN HANDLER",
                exc_info=True)
            sock.send_multipart([constants.PROTO_STATUS_FAILURE, ""])


def _process_call(request_parts):
    """Process single remote call."""
    cmd, body = request_parts

    if cmd != constants.PROTO_CMD_CALL:
        return protocol.response_to_wire(constants.ERROR_BAD_REQUEST,
            "Unknown command: %s" % cmd, None)

    try:
        request = protocol.request_from_wire(body)
    except exceptions.BadRequest as err:
        return protocol.response_to_wire(err.code, str(err), None)

    try:
        service = interfaces.registry[request.interface]
    except KeyError:
        return protocol.response_to_wire(constants.ERROR_BAD_REQUEST,
            "Unsupported interface: %s" % request.interface, None)

    component = service.__interface__

    try:
        result = component.invoke_with_request(request)
    except exceptions.Error as err:
        err_code = err.code or constants.ERROR_UNKNOWN
        return protocol.response_to_wire(err_code, str(err), None,
            request.session.session_id)
    except Exception as err:
        utils.logger().exception("FAILED CALL TO %s.%s",
            request.interface, request.method)
        return protocol.response_to_wire(constants.ERROR_UNKNOWN,
            "Unknown error during request", None,
            request.session.session_id)

    return protocol.response_to_wire(0, None, result,
        request.session.session_id)
