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

"""Server code for JSON-over-ZeroMQ."""

import zmq
from zmq import eventloop

from .. import constants, utils

from . import call, common


def ioloop():
    """Returns 0MQ *IOLoop* instance for current event loop.

    Roughly equivalent to::

        zmq.eventloop.IOLoop.instance()

    """
    return eventloop.IOLoop.instance()


def setup_ioloop(address):
    """Setup io loop for working as a server on given *address*."""
    sock = common.context.socket(zmq.REP)
    sock.bind(address)
    ioloop().add_handler(sock, _message_handler, ioloop().READ)


# Private


def _message_handler(sock, *args):    # pylint: disable-msg=W0613
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

            utils.logger().debug("REQUEST %s%s", request_parts[:2],
                " + attachment" if len(request_parts) > 2 else "")

            response_parts = _command(*request_parts)

            utils.logger().debug("RESPONSE %s%s", response_parts[:2],
                " + attachment" if len(response_parts) > 2 else "")

            sock.send_multipart(response_parts)
        except:  # pragma: no cover
            utils.logger().critical("EXCEPTION IN HANDLER",
                exc_info=True)
            sock.send_multipart([constants.PROTO_STATUS_FAILURE, ""])


def _command(command_name, json_body, *other_parts):
    """Envelop for command."""
    try:
        command_callable = _COMMANDS[command_name]
    except KeyError:
        return [constants.PROTO_STATUS_SUCCESS,
            _BASE.response_to_wire(constants.ERROR_BAD_REQUEST,
                "Unknown command: %s" % command_name)]

    return [constants.PROTO_STATUS_SUCCESS,
        command_callable.process_request(json_body, *other_parts)]


_BASE = common.BaseCommand()

_COMMANDS = {
    constants.PROTO_CMD_CALL: call.CallCommand()
}
