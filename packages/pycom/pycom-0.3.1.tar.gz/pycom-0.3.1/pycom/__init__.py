#   PyCOM - Distributed Component Model for Python
#   Copyright (c) 2011-2012, Dmitry "Divius" Tantsur
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
# - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above
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

"""PyCOM root package."""

from .constants import (
    __version__,        # Python standard version definition
    __version_info__,   # Python standard version definition
    )

from .exceptions import (
    Error,                  # Base exception
    MethodNotFound,         # Remote method not found
    ServiceNotFound,        # Remote service not found
    RemoteError,            # Exception on remote side
    BadRequest,             # Client issued invalid request
    ServiceNotAvailable,    # Remote service not available
    ConfigurationError,     # Error in configuration
    )

from .base import (
    BaseComponent,      # ABC for components
    Request,            # Request structure
    configuration,      # Dictionary with configuration (do not alter directly)
    configure,          # Safe way to alter configuration
    )

from .interfaces import (
    interface,          # Decorator for interfaces
    method,             # Decorator for methods
    )

from .protocol import (
    RemoteComponent,    # Remote component implementation
    )

from .nsclient import (
    locate,             # Locate service on network
    nameserver,         # Function to locate nameserver
    )

from .launcher import (
    ioloop,             # IOLoop instance for a service
    main,               # Main loop for a service
    )
