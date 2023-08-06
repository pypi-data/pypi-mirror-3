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

"""Main routine implementation."""

import logging
from optparse import OptionParser

from six import iterkeys

from . import base, constants, exceptions, interfaces, nsclient
from . import server, utils


def main(argv=None):
    """Starts main loop for a service.

    Raises :exc:`pycom.ConfigurationError` if not configured properly -
    see :doc:`config` for details.

    if *argv* is not None, options parser is used to get options from it.
    Example (from `pycom-launcher` utility)::

        import sys
        import pycom
        pycom.main(sys.argv[1:])

    Returns 0MQ IOLoop exit code.

    """
    address = base.configuration.get("address")
    service = base.configuration.get("service")

    if argv is not None:
        parser = OptionParser()
        parser.add_option("-a", "--address", action="store", dest="address",
            help="Physical ZeroMQ address to listen on",
            default=address)
        parser.add_option("-s", "--service", action="store", dest="service",
            help="Service name",
            default=service)
        parser.add_option("-v", "--verbose", action="store_const",
            dest="verbosity",
            help="Be as verbose as possible",
            const=logging.DEBUG)
        (options, args) = parser.parse_args(args=argv)

        address = options.address
        service = options.service

        if not len(args):
            parser.error("Expected at least one positional argument: module")

        for module_name in args:
            try:
                __import__(module_name)
            except ImportError:
                parser.error("Cannot import module " + module_name)

        utils.logger().setLevel(options.verbosity or logging.INFO)

    if address is None:
        raise exceptions.ConfigurationError("Set address in the configuration")

    if service is None:
        raise exceptions.ConfigurationError("Set service in the configuration")

    ns_component = nsclient.nameserver()
    for interface in iterkeys(interfaces.registry):
        ns_component.invoke(constants.NS_METHOD_REGISTER, args={
            "address": address,
            "interface": interface,
            "service": service
        })

    server.setup_ioloop(address)

    utils.logger().info("PyCOM v%s (service '%s' on '%s')",
        constants.__version__, service, address)
    try:
        return server.ioloop().start()
    except KeyboardInterrupt:  # pragma: no cover
        utils.logger().info("Got KeyboardInterrupt, exiting")
