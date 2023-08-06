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

from . import constants, exceptions, prepare, run, utils


class CallCommand(prepare.PrepareCommand, run.RunCommand):
    """CALL command implementation.

    Inherits :class:`pycom.zerojson.prepare.PrepareCommand`
    and :class:`pycom.zerojson.prepare.RunCommand`.

    """

    request_to_dict = prepare.PrepareCommand.request_to_dict
    request_from_dict = prepare.PrepareCommand.request_from_dict
    response_to_dict = run.RunCommand.response_to_dict
    response_from_dict = run.RunCommand.response_from_dict

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
