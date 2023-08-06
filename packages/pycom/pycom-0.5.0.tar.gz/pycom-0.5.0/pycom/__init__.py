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

# Aliases from ZeroJSON

from zerojson import (
    RemoteError,            # Exception on remote side
    MethodNotFound,         # Remote method not found
    ServiceNotFound,        # Remote service not found
    BadRequest,             # Client issued invalid request
    AccessDenied,           # Access denied to this function
    ServiceNotAvailable,    # Remote service not available
    SessionExpired,         # Client session has expired
    create_task,            # Create repeatable task
    ioloop,                 # IOLoop instance for a service
    )

# Our own imports

from .constants import (
    __version__,        # Python standard version definition
    __version_info__,   # Python standard version definition
    )

from .utils import (
    logger,             # Python logger for PyCOM
    )

from .base import (
    BaseComponent,          # ABC for components
    ConfigurationError,     # Error in configuration
    configuration,      # Dictionary with configuration (do not alter directly)
    configure,              # Safe way to alter configuration
    )

from .helpers import (
    Service,            # Service base class
    interface,          # Decorator for interfaces
    method,             # Decorator for methods
    )

from .nsclient import (
    Context,            # Client context object
    )

from .launcher import (
    main,               # Main loop for a service
    )

from .proxy import (
    ProxyComponent,     # Proxying component
    ProxyContext,       # Proxying context
    )
