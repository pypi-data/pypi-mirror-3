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

"""Client code for JSON-over-ZeroMQ."""

from six import string_types
import zmq

from . import call, common, constants, exceptions


class Client(object):
    """Client component working over 0MQ network.

    Takes 0MQ socket or address as *socket* and interface name as *iface*.
    Optionally takes client *context*.

    """

    def __init__(self, socket, iface):
        """Builds remote component."""
        super(Client, self).__init__()
        if isinstance(socket, string_types):
            self.socket = common.context.socket(zmq.REQ)
            try:
                self.socket.connect(socket)
            except zmq.ZMQError as err:
                if err.errno == zmq.EINVAL:
                    raise ValueError("Invalid address: %s" % socket)
                else:
                    raise exceptions.ServiceNotAvailable(
                        "Service '%s' not available: %s" %
                        (iface, str(err)))
        else:
            self.socket = socket

        self.iface = iface
        self.session_id = None
        self.call_command = call.CallCommand()

    def close(self, **kwargs):
        """Closes accociated socket.

        *kwargs* are passed to underlying 0MQ method.

        """
        self.socket.close(**kwargs)

    def invoke(self, method_name, args=None, timeout=None, attachment=None):
        """Invoke given method with args
        (see :meth:`pycom.BaseComponent.invoke` for details)."""
        response = self.invoke_with_request(
            common.Request(self.iface, method_name, args=args,
                attachment=attachment),
            timeout=timeout)

        if response.attachment is not None:
            return response.result, response.attachment
        else:
            return response.result

    def invoke_with_request(self, request, timeout=None):
        """Invoke method using given request object.

        Returns :class:`zerojson.Response` object.

        """
        message = self.call_command.request_to_wire(request,
            session_id=self.session_id)
        timeout = timeout or constants.PROTO_DEFAULT_TIMEOUT

        result = self._send_message(constants.PROTO_CMD_CALL, message,
            timeout, attachment=request.attachment)
        status, message = result[:2]

        if status != constants.PROTO_STATUS_SUCCESS:
            # Global protocol failure - world is going to explode!
            # This DOESN'T handle normal server-side exceptions
            raise exceptions.ServiceNotAvailable("Service with interface '%s' "
                "is failing" % self.iface)

        try:
            response = self.call_command.response_from_wire(message)
        except exceptions.RemoteError as err:
            if err.code == constants.ERROR_METHOD_NOT_FOUND:
                raise exceptions.MethodNotFound("Method '%s' not found in "
                    "interface %s" % (request.method, self.iface))
            else:
                raise

        if response.session_id is not None:
            self.session_id = response.session_id

        if len(result) > 2:
            response.attachment = result[2]

        return response

    # Private

    def _send_message(self, command, message, timeout, attachment=None):
        """Send prepared message (a list) over wire."""
        if not self.socket.poll(timeout=timeout, flags=zmq.POLLOUT):
            # Timeout - assume peer is disconnected
            raise exceptions.ServiceNotAvailable("Service with interface '%s' "
                "is no longer available" % self.iface)

        request_parts = [command, message]
        if attachment is not None:
            request_parts.append(attachment)

        try:
            self.socket.send_multipart(request_parts, flags=zmq.NOBLOCK,
                copy=False)
        except zmq.ZMQError as err:
            if err.errno == zmq.EAGAIN:
                raise exceptions.ServiceNotAvailable(
                    "Service with interface '%s' is no longer available"
                        % self.iface)
            else:
                raise

        if not self.socket.poll(timeout=timeout):
            raise exceptions.ServiceNotAvailable("Service with interface '%s' "
                "is no longer available" % self.iface)

        try:
            return self.socket.recv_multipart(flags=zmq.NOBLOCK)
        except zmq.ZMQError as err:
            if err.errno == zmq.EAGAIN:
                raise exceptions.ServiceNotAvailable(
                    "Service with interface '%s' is no longer available"
                        % self.iface)
            else:
                raise
