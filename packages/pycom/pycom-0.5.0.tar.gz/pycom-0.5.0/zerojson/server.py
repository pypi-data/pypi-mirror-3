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

from . import async, call, common, constants, eventloop, utils


class Server(object):
    """Basic server instance.

    Subclass and override *handle_call* to get a working server.

    .. attribute:: commands

        Dictionary 'command name' -> 'command implementation'.

    """

    def __init__(self, addresses):
        """Construct and bind to *addresses*."""
        self._socks = []
        for address in addresses:
            sock = common.context.socket(zmq.ROUTER)
            sock.bind(address)
            self._socks.append(sock)

        self._base = common.BaseCommand(server=self)
        self.commands = {
            constants.PROTO_CMD_CALL: call.CallCommand(server=self)
        }

        self.ioloop = None

    def setup(self, ioloop=None):
        """Setup server on a given event loop."""
        self.ioloop = ioloop or eventloop.ioloop()
        for sock in self._socks:
            self.ioloop.add_handler(sock, self._message_handler,
                self.ioloop.READ)

    def handle_call(self, request):
        """Handle a single call."""
        raise NotImplementedError()  # pragma: no cover

    # Private

    @staticmethod
    def _finish_message(sock, address, response_parts):
        """Finish sending a message."""
        utils.logger().debug("RESPONSE %s%s", response_parts[:2],
            " + attachment" if len(response_parts) > 2 else "")
        sock.send_multipart(address + response_parts)

    def _message_handler(self, sock, *args):    # pylint: disable-msg=W0613
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

                address, request_parts = _split(request_parts)

                utils.logger().debug("REQUEST %s%s", request_parts[:2],
                    " + attachment" if len(request_parts) > 2 else "")

                response_parts = self._command(*request_parts)

                if isinstance(response_parts, async.Future):
                    utils.logger().debug("DEFERRED RESPONSE")
                    response_parts.add_callback(self._finish_message,
                        sock, address)
                    response_parts.prepare(self.ioloop)
                else:
                    self._finish_message(sock, address, response_parts)
            except:  # pragma: no cover
                utils.logger().critical("EXCEPTION IN HANDLER",
                    exc_info=True)
                sock.send_multipart([constants.PROTO_STATUS_FAILURE, ""])

    def _command(self, command_name, json_body, *other_parts):
        """Envelop for command."""
        try:
            command_callable = self.commands[command_name]
        except KeyError:
            return [constants.PROTO_STATUS_SUCCESS,
                self._base.response_to_wire(common.Response(None,
                    code=constants.ERROR_BAD_REQUEST,
                    message="Unknown command: %s" % command_name))]

        response = command_callable.process_request(json_body, *other_parts)
        if isinstance(response, async.Future):
            response.add_callback(lambda resp:
                [constants.PROTO_STATUS_SUCCESS, resp])
            return response

        return [constants.PROTO_STATUS_SUCCESS, response]


# Private


def _split(data):
    """Split 0MQ data on address and data parts."""
    try:
        index = data.index(b"")
    except ValueError:
        return [], data

    return data[:index + 1], data[index + 1:]
