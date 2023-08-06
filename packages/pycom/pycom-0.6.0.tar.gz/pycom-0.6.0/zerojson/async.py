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

"""Asynchronous utilities."""

import functools

from . import constants, utils


class Future(object):
    """Object pointing that request will be fulfilled in the future."""

    __slots__ = ("request", "_callbacks", "_getter", "_ioloop", "_shot")

    def __init__(self, request):
        """Constructor."""
        self.request = request
        self._callbacks = []
        self._getter = None
        self._ioloop = None
        self._shot = False

    def add_callback(self, func, *args, **kwargs):
        """Chain a callback.

        This method is NOT intended for end-users!

        """
        self._callbacks.append(functools.partial(func, *args, **kwargs))

    def response(self, result, attachment=None):
        """Send a result.

        This method is thread-safe.

        """
        if self._getter is not None:
            raise RuntimeError("Response is already set on %s" % repr(self))
        self._getter = functools.partial(self.request.response, result,
            attachment=attachment)
        self._schedule_callbacks()

    def error(self, code, message=None):
        """Send an error.

        This method is thread-safe.

        """
        if self._getter is not None:
            raise RuntimeError("Response is already set on %s" % repr(self))
        self._getter = functools.partial(self.request.error, code,
            message=message)
        self._schedule_callbacks()

    def exception(self):
        """Send an exception.

        This method should only be called from an exception handler.

        This method is thread-safe.

        """
        utils.logger().exception("FAILED CALL TO %s.%s",
            self.request.interface, self.request.method)
        self.error(constants.ERROR_UNKNOWN, "Unknown error during request")

    def prepare(self, ioloop):
        """This method is used by :class:`zerojson.Server` to indicate
            that all callbacks were added."""
        self._ioloop = ioloop
        self._schedule_callbacks()

    # Private

    def _schedule_callbacks(self):
        """Schedule callbacks to be run."""
        if self._ioloop is None or self._shot:
            return

        self._ioloop.add_callback(self._run_callbacks)
        self._shot = True

    def _run_callbacks(self):
        """Return response to server."""
        assert self._callbacks

        result = self._getter()
        for callback in self._callbacks:
            result = callback(result)
