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

"""Base code."""

import json

import zerojson

from . import constants


class BaseComponent(object):
    """Abstract base class for components.

    Any component can be used as a context manager.

    .. attribute:: name

       Interface name.

    Components are NOT thread-safe! Do not share them across threads.

    """

    __slots__ = ("name", "context")

    def __init__(self, interface, context=None):
        """Constructor."""
        self.name = interface
        self.context = context

    def invoke(self, method_name, args=None, timeout=None, attachment=None):
        """Calls *method_name* on a service, passing *args* as argument.

        *args* should be anything JSON-serializable.
        *timeout* can be used to prevent *invoke* from hanging forever.
        *timeout* is in milliseconds and defaults to 5000.

        *attachment* is any binary of type ``bytes``.

        Raises :exc:`pycom.MethodNotFound` if service doesn't provide
        method *method_name*. Raises :exc:`pycom.ServiceNotAvailable`
        if service cannot be reached during request.

        Returns call result as a JSON-serializable entity if there is no
        attachments. If an attachment is present, result is a tuple
        with the first item being JSON result, the second being an attachment.

        """
        request = zerojson.Request(self.name, method_name, args=args,
            attachment=attachment)

        if self.context is not None:
            for hook in self.context.prehooks:
                request = hook(self, request)

        response = self.invoke_with_request(request, timeout=timeout)

        if self.context is not None:
            for hook in self.context.posthooks:
                response = hook(self, response)

        if response.attachment is not None:
            return response.result, response.attachment
        else:
            return response.result

    def invoke_with_request(self, request,
            timeout=None):  # pylint: disable-msg=W0613
        """Invoke method using given request object.

        Must be overriden in a real component class.

        Returns :class:`zerojson.Response` object.

        """
        raise NotImplementedError()  # pragma: no cover

    def close(self):
        """Closes component, if possible."""
        pass  # pragma: no cover

    def introspect(self):
        """Get structure with introspection information.

        See :class:`pycom.Service` for details.

        """
        return self.invoke(constants.GENERIC_METHOD_INTROSPECT)

    __enter__ = lambda self: self

    __exit__ = lambda self, *args: self.close()


class ConfigurationError(Exception):
    """Error found in configuration."""


#: Read-only dictionary with current configuration
configuration = {}


def configure(*args, **kwargs):
    """Safe way to alter configuration.

    The only position argument should be a JSON file.
    Keyword arguments are added to global configuration.

    Example::

        import pycom
        pycom.configure(nameserver="tcp://127.0.0.1:2012")

    """
    if len(args) > 0:
        assert len(args) == 1
        _load(args[0])

    configuration.update(kwargs)


# Protected


interface_registry = {}  #: Local interfaces registry.


# Private


def _load(file_name):
    """Load configuration from JSON file."""
    with open(file_name, "rt") as conf_file:
        configuration.update(json.load(conf_file))
