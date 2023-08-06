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

from . import constants, nsclient


class ProxyContext(object):
    """Context object with handy access to methods."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self._wrapped = nsclient.Context(*args, **kwargs)

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

        results = method_info["results"]
        if len(results) > 1:
            result_type = collections.namedtuple("ResultType",
                " ".join(method_info["results"]))

        required_argument = method_info["required_arguments"]
        del method_info

        def _call(*args, **kwargs):  # pylint: disable-msg=C0111
            if len(args) > len(required_argument):
                raise TypeError("Too many positional arguments, expected %d" %
                    len(required_argument))

            for arg, value in zip(required_argument, args):
                if arg in kwargs:
                    raise TypeError("Argument '%s' got multiple values" % arg)
                kwargs[arg] = value

            for arg in required_argument:
                if arg not in kwargs:
                    raise TypeError("Argument '%s' is required" % arg)

            result = self._wrapped.invoke(name, args=kwargs)

            if len(results) > 1:
                return result_type._make(  # pylint: disable-msg=W0212
                    result[item] for item in results)
            elif len(results) == 1:
                return result[results[0]]
            else:
                return result

        return _call
