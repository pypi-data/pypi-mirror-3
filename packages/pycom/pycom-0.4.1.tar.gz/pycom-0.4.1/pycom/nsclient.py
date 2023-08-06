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

from . import base, constants, exceptions, interfaces, zerojson


def nameserver():
    """Get nameserver component with default context.

    This function uses global context, thus is not thread-safe.
    See :meth:`pycom.Context.nameserver`.

    """
    return _default_context.nameserver()


def locate(*args, **kw):
    """Locate a service with default context.

    This function uses global context, thus is not thread-safe.
    See :meth:`pycom.Context.locate`.

    """
    return _default_context.locate(*args, **kw)


class Context(object):
    """Context is a main high-level class for accessing components.

    .. attribute:: extensions

       Dictionary with extensions data that should be
       passed with every request.

    """

    def __init__(self):
        """Constructor."""
        self.extensions = {}
        self._ns_component = None

    def nameserver(self):
        """Get nameserver component."""
        if self._ns_component is not None:
            return self._ns_component

        ns_conf = base.configuration.get("nameserver", constants.NS_NAME_LOCAL)
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

        return zerojson.RemoteComponent(info["address"], iface)


# Private

_default_context = Context()


# Following functions exists only for tests!

def _pop_cached_ns(ctx=_default_context):
    """Drop cached nameserver and return it."""
    result = ctx._ns_component  # pylint: disable-msg=W0212
    ctx._ns_component = None
    return result


def _restore_cached_ns(new_ns, ctx=_default_context):
    """Restore cached nameserver."""
    ctx._ns_component = new_ns
