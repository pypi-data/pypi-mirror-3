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

"""Exceptions."""

from . import constants


class Error(Exception):
    """Base class for PyCOM exceptions."""

    code = None


class MethodNotFound(Error):
    """Remote method not found."""

    code = constants.ERROR_METHOD_NOT_FOUND


class ServiceNotFound(Error):
    """Remote service not found."""

    code = constants.ERROR_SERVICE_NOT_FOUND


class BadRequest(Error):
    """Client sent bad request."""

    code = constants.ERROR_BAD_REQUEST


class ServiceNotAvailable(Error):
    """Remote service not available."""


class RemoteError(Error):
    """User exception on a remote side.

    The following attribute is set from the constructor:

    .. attribute:: code

        Exception code.

    """

    def __init__(self, msg, code=None):
        """C-tor."""
        super(RemoteError, self).__init__(msg)
        self.code = code


class ConfigurationError(Error):
    """Error found in configuration."""
