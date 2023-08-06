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
import uuid


class Request(object):
    """Request object.

    .. attribute:: interface

       Current interface name

    .. attribute:: method

       Current method name

    .. attribute:: session

       Session for current component - dict-like object of
       type :class:`pycom.base.Session`

    .. attribute:: args

       Arguments passed by client side as Python object

    """

    __slots__ = ("interface", "method", "session", "args")

    def __init__(self, interface, method, session, args):
        """Initializer."""
        self.interface = interface
        self.method = method
        self.session = session
        self.args = args

    def response(self, result):  # pylint: disable-msg=R0201
        """Build response object to return from method.

        *result* is a JSON-serializable entity to return to client.

        """
        return result


class BaseComponent(object):
    """Abstract base class for components."""

    __slots__ = ()

    def invoke(self, method_name, args=None,
            timeout=None):  # pylint: disable-msg=W0613
        """Calls *method_name* on a service, passing *args* as argument.

        *args* should be anything JSON-serializable.
        *timeout* can be used to prevent *invoke* from hanging forever.
        *timeout* is in milliseconds and defaults to 5000.

        Raises :exc:`pycom.MethodNotFound` if service doesn't provide
        method *method_name*. Raises :exc:`pycom.ServiceNotAvailable`
        if service cannot be reached during request.

        Returns call result as a JSON-serializable entity.

        """
        raise NotImplementedError()  # pragma: no cover

    def close(self):
        """Closes component, if possible."""
        pass  # pragma: no cover


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


class Session(dict):
    """Class representing session.

    Inherits from `dict`, provides one additional attribute:

    .. attribute: session_id

       UUID of session

    """

    def __init__(self, session_id, *args, **kw):
        """Constructor."""
        super(Session, self).__init__(*args, **kw)
        self.session_id = session_id


class Call(dict):
    """Class representing single remote call.

    Inherits from `dict`, provides one additional attribute:

    .. attribute: call_id

       UUID of call

    """

    def __init__(self, call_id, *args, **kw):
        """Constructor."""
        super(Call, self).__init__(*args, **kw)
        self.call_id = call_id


class UUIDFactory(object):
    """Factory responsible for creating objects with UUID."""

    def __init__(self, items_factory):
        """Initialize empty factory."""
        self._items = {}
        self._items_factory = items_factory

    def new(self):
        """Create new session object and return it."""
        unique_id = uuid.uuid1().hex
        self._items[unique_id] = self._items_factory(unique_id)
        return self._items[unique_id]

    def get(self, unique_id):
        """Fetch existing item by it's ID.

        Raises `KeyError` on failure.

        """
        return self._items[unique_id]


# Private


def _load(file_name):
    """Load configuration from JSON file."""
    with open(file_name, "rt") as conf_file:
        configuration.update(json.load(conf_file))
