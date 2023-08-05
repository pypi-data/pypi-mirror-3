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

"""Support for invoking."""

import zmq

from six import string_types

from . import exceptions, protocol


class DirectInvoker(object):
    """Proxy invokers that directly calls object's methods."""

    def __init__(self, wrapped):
        """C-tor."""
        self.wrapped = wrapped
        try:
            self.interface = wrapped.__interface__
        except AttributeError:
            raise TypeError("Object %s is not declared as an interface" %
                repr(wrapped))

    def invoke(self, method_name, args=None,
            timeout=None):  # pylint: disable-msg=W0613
        """Invoke given method with args.

        timeout is ignored and provided only for
        compatibility with other invokers.

        """
        try:
            method_callable = self.interface.methods[method_name]
        except KeyError:
            raise exceptions.MethodNotFound("Method '%s' not found in "
                "interface %s" % (method_name, self.interface.name))

        return method_callable(self.wrapped,
            protocol.Request(self.interface.name, method_name, args))


class RemoteInvoker(object):
    """Invoker over 0MQ network."""

    def __init__(self, socket, iface):
        """C-tor. Takes 0MQ socket or address and interface name."""
        if isinstance(socket, string_types):
            self.socket = protocol.context.socket(zmq.REQ)
            self.socket.connect(socket)
        else:
            self.socket = socket

        self.iface = iface

    def invoke(self, method_name, args=None,
            timeout=None):
        """Invoke given method with args.

        timeout should be in milliseconds if present.

        """
        return protocol.send_request(self.socket, self.iface, method_name,
            args, timeout=timeout)
