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

"""Common constants."""

###BEGIN - here starts self-documenting part to include into Sphinx docs

# Versions

__version_info__ = (0, 6, 0, "")
__version__ = "%d.%d.%d%s" % __version_info__

# Standard stuff

GENERIC_METHOD_INTROSPECT = "introspect"

# Nameserver constants

NS_INTERFACE = "org.pycom.nameserver"
NS_METHOD_STAT = "stat"
NS_METHOD_LOCATE = "locate"
NS_METHOD_REGISTER = "register"
NS_METHOD_LIST_SERVICES = "list_services"
NS_SERVICE_TIMEOUT = 60000

# Authenticator constants

AUTH_INTERFACE = "org.pycom.authenticator"
AUTH_METHOD_AUTHENTICATE = "authenticate"
AUTH_METHOD_VALIDATE = "validate"
AUTH_EXTENSION = "org.pycom.auth"

# Other constants

NS_NAME_LOCAL = "local"

###END - here ends self-documenting part to include into Sphinx docs
