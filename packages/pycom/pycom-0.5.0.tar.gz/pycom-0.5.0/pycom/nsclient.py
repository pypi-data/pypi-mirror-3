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

"""Synchronous client API for PyCOM nameserver."""

import copy

import zerojson

from . import base, constants, interfaces


class Context(object):
    """Context is a main high-level class for accessing components.

    If *nameserver* is not present, uses global configuration.

    .. attribute:: prehooks
    .. attribute:: posthooks

       Lists of hooks that should be executed for pre- and post- processing
       incoming and outgoing data. Hook is a callable with the following
       signature:

        .. function:: hook(component, data)

           .. attribute:: component
              :noindex:

              Remote or local component

           .. attribute:: data
              :noindex:

              Data to be processed (:class:`zerojson.Request` for prehooks,
              :class:`zerojson.Response` for posthooks).

    """

    def __init__(self, nameserver=None):
        """Constructor."""
        self.prehooks = []
        self.posthooks = []
        self._ns_component = None
        self._ns_hint = nameserver

    def nameserver(self):
        """Get nameserver component."""
        if self._ns_component is not None:
            return self._ns_component

        if self._ns_hint is not None:
            ns_conf = self._ns_hint
        else:
            ns_conf = base.configuration.get("nameserver",
                constants.NS_NAME_LOCAL)

        if ns_conf == constants.NS_NAME_LOCAL:
            try:
                ns_instance = interfaces.registry[constants.NS_INTERFACE]
            except KeyError:
                ns_instance = None

            if ns_instance is not None:
                # Shallow copy of a component
                self._ns_component = copy.copy(ns_instance.__interface__)
                self._ns_component.context = self
            else:
                raise zerojson.ServiceNotFound("Nameserver not found")
        else:
            self._ns_component = detect_ns(ns_conf)

        return self._ns_component

    def locate(self, iface, service_name=None):
        """Locate a service providing given interface *iface*.

        If *service_name* is specified,
        only service with this name will be returned.

        """
        ns_component = self.nameserver()
        try:
            info = ns_component.invoke(constants.NS_METHOD_LOCATE,
                {"interface": iface, "service": service_name})
        except zerojson.RemoteError as err:
            if err.code == zerojson.constants.ERROR_SERVICE_NOT_FOUND:
                raise zerojson.ServiceNotFound(
                    "Service with interface '%s' not found" % iface)
            else:
                raise

        return self.connect(info["address"], iface)

    def connect(self, address, iface):
        """Connect to a service providing *iface* on a given *address*."""
        return RemoteComponent(address, iface, context=self)


# Protected


class RemoteComponent(base.BaseComponent):
    """Client component working over 0MQ network."""

    def __init__(self, address, iface, context=None):
        """Constructor."""
        super(RemoteComponent, self).__init__(iface, context=context)
        self._wrapped = zerojson.Client(address, iface)

    def invoke_with_request(self, request, timeout=None):
        """Invoke method using given request object.

        Returns :class:`zerojson.Response` object.

        """
        return self._wrapped.invoke_with_request(request, timeout=None)

    def close(self, **kwargs):
        """Closes component, if possible."""
        return self._wrapped.close(**kwargs)


def detect_ns(host):
    """Detect nameserver on a given *host*."""
    try:
        ns_component = RemoteComponent(host, constants.NS_INTERFACE)
    except zerojson.ServiceNotAvailable:
        raise zerojson.ServiceNotFound("Nameserver not available")
    except ValueError as err:
        assert "Invalid address" in str(err), str(err)
        raise base.ConfigurationError(
            "Invalid nameserver address: %s" % host)

    try:
        ns_component.invoke(constants.NS_METHOD_STAT)
    except zerojson.ServiceNotAvailable:
        ns_component.close(linger=0)
        raise zerojson.ServiceNotFound("Nameserver not available")

    return ns_component


# Private


# Following functions exist only for tests!

def _pop_cached_ns(ctx):
    """Drop cached nameserver and return it."""
    result = ctx._ns_component  # pylint: disable-msg=W0212
    ctx._ns_component = None
    return result


def _restore_cached_ns(new_ns, ctx):
    """Restore cached nameserver."""
    ctx._ns_component = new_ns
