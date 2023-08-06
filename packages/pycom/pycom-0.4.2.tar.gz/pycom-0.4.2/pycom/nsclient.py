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

import warnings

from . import base, constants, exceptions, interfaces, zerojson


def nameserver():   # pragma: no cover
    """Get nameserver component with default context.

    Deprecated, do not use.

    """
    warnings.warn("pycom.nameserver() is deprecated, use pycom.Context",
        stacklevel=2)
    return _default_context.nameserver()


def locate(*args, **kw):   # pragma: no cover
    """Locate a service with default context.

    Deprecated, do not use.

    """
    warnings.warn("pycom.locate() is deprecated, use pycom.Context",
        stacklevel=2)
    return _default_context.locate(*args, **kw)


class Context(object):
    """Context is a main high-level class for accessing components.

    If *nameserver* is not present, uses global configuration.

    """

    def __init__(self, nameserver=None):
        """Constructor."""
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
                ns_instance = interfaces.registry[constants.IFACE_NAMESERVER]
            except KeyError:
                ns_instance = None

            if ns_instance is not None:
                self._ns_component = ns_instance.__interface__
            else:
                raise exceptions.ServiceNotFound("Nameserver not found")
        else:
            self._ns_component = zerojson.detect_ns(ns_conf)

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
        except exceptions.RemoteError as err:
            if err.code == constants.ERROR_SERVICE_NOT_FOUND:
                raise exceptions.ServiceNotFound(
                    "Service with interface '%s' not found" % iface)
            else:
                raise

        return self.connect(info["address"], iface)

    def connect(self, address, iface):
        """Connect to a service providing *iface* on a given *address*."""
        return zerojson.RemoteComponent(address, iface, context=self)

# Private

_default_context = Context()    # Deprecated


# Following functions exist only for tests!

def _pop_cached_ns(ctx=_default_context):
    """Drop cached nameserver and return it."""
    result = ctx._ns_component  # pylint: disable-msg=W0212
    ctx._ns_component = None
    return result


def _restore_cached_ns(new_ns, ctx=_default_context):
    """Restore cached nameserver."""
    ctx._ns_component = new_ns
