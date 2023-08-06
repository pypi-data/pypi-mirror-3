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


# Exceptions that can be raised by remote side


class RemoteError(Exception):
    """User exception on a remote side.

    The following attribute is set from the constructor:

    .. attribute:: code

        Exception code.

    Base class for any exceptions that can be raised by remote side.

    """

    code = constants.ERROR_UNKNOWN

    def __init__(self, msg, code=None):
        """C-tor."""
        super(RemoteError, self).__init__(msg)
        if code is not None:
            self.code = code


class MethodNotFound(RemoteError):
    """Remote method not found."""

    code = constants.ERROR_METHOD_NOT_FOUND


class ServiceNotFound(RemoteError):
    """Remote service not found."""

    code = constants.ERROR_SERVICE_NOT_FOUND


class BadRequest(RemoteError):
    """Client sent bad request."""

    code = constants.ERROR_BAD_REQUEST


class AccessDenied(RemoteError):
    """Access denied to this function."""

    code = constants.ERROR_ACCESS_DENIED


class SessionExpired(RemoteError):
    """Client session has expired."""

    code = constants.ERROR_SESSION_EXPIRED


# Local-only exceptions


class ServiceNotAvailable(Exception):
    """Remote service not available."""
