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

"""CALL command implementation."""

from . import common, constants, exceptions, utils


class CallCommand(common.BaseCommand):
    """CALL command implementation."""

    # pylint: disable-msg=W0221

    def request_to_dict(self, request, session_id=None):
        """Dump request to Python dict."""
        result = {
            "interface": request.interface,
            "method": request.method,
            "session_id": session_id,
            "args": request.args
        }

        if request.extensions:
            result["extensions"] = request.extensions

        return result

    def request_from_dict(self, data):
        """Get request from Python dict."""
        session_id = data.get("session_id", None)

        if session_id is None:
            session = self.session_factory.new()
            utils.logger().debug("NEW SESSION '%s'", session.session_id)
        else:
            try:
                session = self.session_factory.get(session_id)
            except KeyError:
                raise exceptions.SessionExpired("Session '%s' has expired" %
                    session_id)

        try:
            return common.Request(data["interface"], data["method"],
                session=session, args=data.get("args"),
                extensions=data.get("extensions"))
        except KeyError as err:
            raise exceptions.BadRequest("Field %s is required" % err.args[0])

    def response_to_dict(self, response):
        """Dump response to Python dict."""
        result = {
            "session_id": response.session_id
        }

        if not response.code:
            result["result"] = response.result

        if response.extensions:
            result["extensions"] = response.extensions

        return result

    def response_from_dict(self, data):
        """Get request from Python dict."""
        return common.Response(None, result=data.get("result"),
            session_id=data.get("session_id"),
            extensions=data.get("extensions"))

    # pylint: enable-msg=W0221

    def real_process_request(self, request, *other_parts):
        """Call to process request."""
        if other_parts:
            return request.error(constants.ERROR_BAD_REQUEST,
                message="Expected two parts, got %d" % (len(other_parts) + 2))

        try:
            response = self.server.handle_call(request)
        except exceptions.RemoteError as err:
            return request.error(err.code or constants.ERROR_UNKNOWN,
                message=str(err))
        except Exception:
            utils.logger().exception("FAILED CALL TO %s.%s",
                request.interface, request.method)
            return request.error(constants.ERROR_UNKNOWN,
                message="Unknown error during request")

        return response
