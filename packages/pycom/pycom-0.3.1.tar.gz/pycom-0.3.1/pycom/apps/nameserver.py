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

"""Nameserver service."""

import collections

from six import itervalues

import pycom
from pycom import constants


@pycom.interface(constants.IFACE_NAMESERVER)
class NameServer(object):
    """Class representing nameserver for PyCOM."""

    @pycom.method(constants.NS_METHOD_STAT)
    def method_stat(self, request):  # pylint: disable-msg=W0613,R0201
        """Ping method. Will return some statistics in the future."""
        return {}

    @pycom.method(constants.NS_METHOD_REGISTER)
    def method_register(self, request):
        """Register service."""
        try:
            address = request.args["address"]
            interface = request.args["interface"]
            service = request.args["service"]
        except (KeyError, TypeError):
            raise pycom.BadRequest("Following field are mandatory: "
                "address, interface, service")

        if interface not in self._registry:
            self._registry[interface] = []

        rec = _Record(address, interface, service)
        self._registry[interface].append(rec)
        self._services[service] = rec

        return {}

    @pycom.method(constants.NS_METHOD_LOCATE)
    def method_locate(self, request):
        """Locate service."""
        try:
            interface = request.args["interface"]
        except (KeyError, TypeError):
            raise pycom.BadRequest("Following field are mandatory: "
                "interface")

        try:
            records = self._registry[interface]
        except KeyError:
            raise pycom.ServiceNotFound("Interface not found: %s" %
                interface)

        service = request.args.get("service")
        full_list = [
            {
                "address": record.address,
                "service": record.service
            }
            for record in records
            if service is None or record.service == service
        ]

        assert len(full_list)

        if request.args.get("as_list"):
            return full_list
        else:
            return full_list[0]

    @pycom.method(constants.NS_METHOD_LIST_SERVICES)
    def method_list_services(self, request):    # pylint: disable-msg=W0613
        """List all services."""
        return [
            {
                "service": rec.service,
                "interface": rec.interface
            }
            for rec in itervalues(self._services)
        ]

    # Private

    _registry = {}
    _services = {}


# Private


class _Record(collections.namedtuple("Record", "address interface service")):
    """Class representing a record."""
