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

"""IOLoop for ZeroJSON."""

import datetime
import functools
import uuid

from zmq.eventloop import ioloop as zmq_ioloop

from . import utils


def ioloop():
    """Returns 0MQ *IOLoop* instance for current event loop.

    Roughly equivalent to::

        zmq.eventloop.IOLoop.instance()

    """
    return zmq_ioloop.IOLoop.instance()


def create_task(callback, timeout):
    """Create repeating task."""
    return zmq_ioloop.PeriodicCallback(callback, timeout, ioloop())


class UUIDFactory(object):
    """Factory responsible for creating objects with UUID."""

    def __init__(self, items_factory):
        """Initialize empty factory."""
        self._items = {}
        self._items_factory = items_factory

    def new(self):
        """Create new session object and return it."""
        unique_id = uuid.uuid1().hex
        self._items[unique_id] = self._items_factory(unique_id,
            session_factory=self)
        return self.get(unique_id)  # Allow for overloading

    def get(self, unique_id):
        """Fetch existing item by it's ID.

        Raises `KeyError` on failure.

        """
        return self._items[unique_id]

    def drop(self, unique_id):
        """Drop existing item by it's ID."""
        del self._items[unique_id]


class ExpiringFactory(UUIDFactory):
    """UUID factory whose members can expire."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self._timeout = kwargs.pop("timeout")
        self._message = kwargs.pop("message", "Object '%s' expired")
        super(ExpiringFactory, self).__init__(*args, **kwargs)
        self._callbacks = {}

    def get(self, unique_id):
        """Fetch existing item by it's ID."""
        item = super(ExpiringFactory, self).get(unique_id)

        try:
            callback = self._callbacks[unique_id]
        except KeyError:
            pass
        else:
            ioloop().remove_timeout(callback)

        self._callbacks[unique_id] = ioloop().add_timeout(
            datetime.timedelta(milliseconds=self._timeout),
            functools.partial(self.drop, unique_id))

        return item

    def drop(self, unique_id):
        """Drop existing item by it's ID."""
        super(ExpiringFactory, self).drop(unique_id)
        ioloop().remove_timeout(self._callbacks[unique_id])
        del self._callbacks[unique_id]
        utils.logger().debug(self._message, unique_id)
