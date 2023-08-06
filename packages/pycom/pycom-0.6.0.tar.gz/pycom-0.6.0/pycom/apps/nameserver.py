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
import datetime
import random
import re

from six import itervalues, string_types

import pycom
from pycom.ext import checks


_STRING_AND_NONE = string_types + (None.__class__,)


@pycom.interface(pycom.constants.NS_INTERFACE, authentication="never")
class NameServer(pycom.Service):
    """Class representing nameserver for PyCOM."""

    # pylint: disable-msg=W0613,R0201,C0322

    @pycom.method(pycom.constants.NS_METHOD_STAT)
    def method_stat(self, request):
        """Ping method. Will return some statistics in the future."""
        return {}

    @checks.check_argument("address", valid_types=string_types)
    @checks.check_argument("service", valid_types=string_types)
    @checks.check_argument("interfaces", valid_types=list,
        validator=lambda name, value:
            all(isinstance(item, string_types) for item in value))
    @pycom.method(pycom.constants.NS_METHOD_REGISTER)
    def method_register(self, request, address, interfaces, service):
        """Register service."""
        if service in self._services:
            pycom.ioloop().remove_timeout(self._timeouts[service])

            if self._services[service].address != address:
                raise pycom.AccessDenied(
                    "Service %s already registered on a different address"
                        % service)

            first_time = False
        else:
            first_time = True

        def _expire():
            """Utility to drop a service on timeout."""
            pycom.logger().info("Unregistering service '%s' due to timeout",
                service)
            self._drop_service(service)

        if first_time:
            pycom.logger().info("Registering service '%s'", service)
        else:
            pycom.logger().debug("Renewed service '%s'", service)

        self._drop_service(service)

        rec = _Record(address, interfaces, service)
        self._services[service] = rec

        for interface in interfaces:
            self._registry[interface].add(service)
            if first_time:
                pycom.logger().info(".. interface '%s'", interface)

        self._timeouts[service] = pycom.ioloop().add_timeout(
            datetime.timedelta(
                milliseconds=pycom.constants.NS_SERVICE_TIMEOUT),
            _expire)

        return {}

    @checks.check_argument("interface", valid_types=string_types)
    @checks.check_argument("service", valid_types=_STRING_AND_NONE)
    @pycom.method(pycom.constants.NS_METHOD_LOCATE,
        results=("address", "service", "interfaces"))
    def method_locate(self, request, interface, service=None):
        """Locate service."""
        found = [
            found_service
            for found_service in self._registry[interface]
            if service is None or found_service == service
        ]

        try:
            # Kind of load balancing - select random service
            record = self._services[random.choice(found)]
        except IndexError:
            raise pycom.ServiceNotFound("Interface not found: %s" %
                interface)

        return record.as_tuple()

    @checks.check_argument("interface", valid_types=_STRING_AND_NONE)
    @checks.check_argument("service", valid_types=_STRING_AND_NONE)
    @pycom.method(pycom.constants.NS_METHOD_LIST_SERVICES)
    def method_list_services(self, request, interface=None, service=None):
        """List all services."""
        if interface is not None:
            try:
                interface = re.compile(interface)
            except re.error as err:
                raise pycom.BadRequest("Invalid regular expression in "
                    "argument 'interface': %s" % str(err))

        if service is not None:
            try:
                service = re.compile(service)
            except re.error as err:
                raise pycom.BadRequest("Invalid regular expression in "
                    "argument 'service': %s" % str(err))

        return [
            rec.as_dict()
            for rec in itervalues(self._services)
            if (interface is None
                or any(interface.match(item) for item in rec.interfaces))
            and (service is None
                or service.match(rec.service))
        ]

    # pylint: enable-msg=W0613,R0201,C0322

    # Private

    #: Mapping interface -> set of service names
    _registry = collections.defaultdict(set)
    #: Mapping service name -> _Record
    _services = {}
    #: Mapping service -> timeout ID
    _timeouts = {}

    def _drop_service(self, service):
        """Remove all mentions of given service."""
        for interface in self._registry.copy():
            try:
                self._registry[interface].remove(service)
            except KeyError:
                pass

            if not self._registry[interface]:
                del self._registry[interface]

        try:
            del self._services[service]
        except KeyError:
            pass


# Private


class _Record(object):
    """Class representing a record about service."""

    __slots__ = ("address", "interfaces", "service")

    def __init__(self, address, interfaces, service):
        """Constructor."""
        self.address = address
        self.interfaces = interfaces
        self.service = service

    def as_tuple(self):
        """Convert to a tuple."""
        return self.address, self.service, list(self.interfaces)

    def as_dict(self):
        """Convert to a dict."""
        return {
            "service": self.service,
            "address": self.address,
            "interfaces": list(self.interfaces)
        }
