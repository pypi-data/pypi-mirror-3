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

"""Protocol constants."""

###BEGIN - here starts self-documenting part to include into Sphinx docs

# Versions

__version_info__ = (0, 5, 0, "")
__version__ = "%d.%d.%d%s" % __version_info__

# Error codes

ERROR_UNKNOWN = 1
ERROR_METHOD_NOT_FOUND = 2
ERROR_SERVICE_NOT_FOUND = 3
ERROR_BAD_REQUEST = 4
ERROR_ACCESS_DENIED = 5
ERROR_SESSION_EXPIRED = 6

# Protocol constants

PROTO_VERSION = "1.0"
PROTO_CMD_CALL = b"CALL"
PROTO_CMD_FINISH = b"FINISH"
PROTO_STATUS_SUCCESS = b"OK"
PROTO_STATUS_FAILURE = b"FAIL"
PROTO_DEFAULT_TIMEOUT = 5000
PROTO_SESSION_TIMEOUT = 3600 * 1000  # 1hr in ms

###END - here ends self-documenting part to include into Sphinx docs
