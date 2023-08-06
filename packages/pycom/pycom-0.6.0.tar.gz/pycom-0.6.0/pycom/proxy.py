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

"""Proxy Context API."""

import collections
import functools

from . import constants, nsclient


class ProxyContext(object):
    """Context object with handy access to methods.

    Can also be used to wrap a real :class:`pycom.Context` object, e.g.::

        ctx = pycom.Context()
        # ...
        proxy_ctx = pycom.ProxyContext(ctx)

    """

    def __init__(self, *args, **kwargs):
        """Constructor."""
        if args and isinstance(args[0], nsclient.Context):
            self._wrapped = args[0]
        else:
            self._wrapped = nsclient.Context(*args, **kwargs)

    def __getattr__(self, name):
        """Pass calls to a real context."""
        return getattr(self._wrapped, name)

    def nameserver(self, *args, **kwargs):
        """Locate a service, return proxying component.

        See :meth:`pycom.Context.nameserver`.

        """
        return ProxyComponent(self._wrapped.nameserver(*args, **kwargs))

    def locate(self, *args, **kwargs):
        """Locate a service, return proxying component.

        See :meth:`pycom.Context.locate`.

        """
        return ProxyComponent(self._wrapped.locate(*args, **kwargs))

    def connect(self, *args, **kwargs):
        """Connect to a service, return proxying component.

        See :meth:`pycom.Context.connect`.

        """
        return ProxyComponent(self._wrapped.connect(*args, **kwargs))


class ProxyComponent(object):
    """Component that passes Python method calls as remote method calls.

    Examples::

        import pycom

        context = pycom.ProxyContext(nameserver="tcp://127.0.0.1:2012")
        with context.locate("org.pycom.nameserver") as proxy:
            services = proxy.list_services()
            services = proxy.list_services(interface="org.pycom.nameserver")

            service = proxy.locate("org.pycom.nameserver")
            service = proxy.locate(interface="org.pycom.nameserver")
            service = proxy.locate("org.pycom.nameserver",
                service="/org/pycom/nameserver")
            service = proxy.locate(interface="org.pycom.nameserver",
                service="/org/pycom/nameserver")

    Methods with multiple results return `namedtuple`.

    Be careful with attachments: they will NOT work unless properly declared
    using ``attachments`` and ``results`` arguments of :func:`pycom.method`.
    Both attachments are dialed with just like any other argument.

    """

    def __init__(self, wrapped):
        """Constructor."""
        self._wrapped = wrapped
        self._methods = wrapped.invoke(
            constants.GENERIC_METHOD_INTROSPECT)["methods"]

    def __enter__(self):
        """Enter context management."""
        return self

    def __exit__(self, *args):
        """Exit context management - close proxy."""
        self._wrapped.close()

    def __getattr__(self, name):
        """Returns proxy method."""
        try:
            method_info = self._methods[name]
        except KeyError:
            raise AttributeError("Method '%s' not found" % name)

        result = functools.partial(_proxy_attribute, name, self._wrapped,
            method_info["required_arguments"], method_info["results"],
            method_info["attachments"])
        result.__name__ = name
        result.__doc__ = method_info.get("docstring") or \
            "Remote method '%s.%s'." % (self._wrapped.name, name)
        return result


# Private


def _proxy_attribute(name, wrapped, required_arguments, results, attachments,
        *args, **kwargs):
    """Callable that handles call to remote method."""
    if len(results) > 1:
        result_type = collections.namedtuple("ResultType", " ".join(results))

    if len(args) > len(required_arguments):
        raise TypeError("Too many positional arguments, expected %d" %
            len(required_arguments))

    for arg, value in zip(required_arguments, args):
        if arg in kwargs:
            raise TypeError("Argument '%s' got multiple values" % arg)
        kwargs[arg] = value

    for arg in required_arguments:
        if arg not in kwargs:
            raise TypeError("Argument '%s' is required" % arg)

    try:
        attachment = kwargs[attachments["incoming"]]
    except KeyError:
        attachment = None

    result = wrapped.invoke(name, args=kwargs, attachment=attachment)

    if isinstance(result, tuple) and attachments["outgoing"] is not None:
        result, attachment = result
        result[attachments["outgoing"]] = attachment

    if len(results) > 1:
        return result_type._make(  # pylint: disable-msg=W0212
            result[item] for item in results)
    elif len(results) == 1:
        return result[results[0]]
    else:
        return result
