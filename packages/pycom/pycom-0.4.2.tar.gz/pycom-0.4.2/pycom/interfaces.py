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

"""Tools for interface declaration."""

import inspect

from six import itervalues

from . import base, exceptions


registry = {}


class Interface(base.BaseComponent):
    """Internal object, representing interface.

    Should not be created directly, only using :func:`pycom.interface`.
    Available through :attr:`__interface__` attribute
    of objects with interface (and their classes).

    Inherits :class:`pycom.BaseComponent`, allows directly calling methods.

    .. attribute:: instance

       Stored owner class instance.

    .. attribute:: name

       Interface name.

    .. attribute:: methods

       Dictionary of methods for this class, keys being method names,
       value being objects of type :class:`pycom.interfaces.Method`.

    """

    __slots__ = ("instance", "name", "methods")

    def __init__(self, wrapped, name):
        """C-tor. Never call it directly, use pycom.interface decorator."""
        super(Interface, self).__init__()

        if name in registry and not isinstance(registry[name], wrapped):
            raise RuntimeError("Interface %s is already registered "
                "for object %s" % (name, repr(registry[name])))

        self.instance = wrapped()
        self.name = name
        self.methods = {}

        for key in dir(wrapped):
            method_info = getattr(getattr(wrapped, key), "__method__", None)
            if method_info is None:
                continue

            self.register_method(method_info)

        for method_info in itervalues(self.methods):
            method_info.post_configure(self)

        registry[name] = self.instance

    def register_method(self, method_info):
        """Register method with descriptor *method_info*
        of type :class:`pycom.interfaces.Method`.

        Raises `RuntimeError` if method with this name is already registered.

        """
        if (method_info.name in self.methods and
                self.methods[method_info.name] is not method_info):
            raise RuntimeError("Function %s is already registered "
                "for interface %s" % (method_info.name, self.name))

        self.methods[method_info.name] = method_info

    def invoke(self, method_name, args=None, **kw):  # pylint:disable-msg=W0613
        """Invoke given method with args
        (see :meth:`pycom.BaseComponent.invoke` for details).

        *timeout* is ignored and provided only for
        compatibility with other components.

        """
        return self.invoke_with_request(
                base.Request(self.name, method_name, None, args)
            ).result

    def invoke_with_request(self, request):
        """Invoke method using given request object.

        Returns :class:`pycom.Response` object.

        """
        try:
            method_info = self.methods[request.method]
        except KeyError:
            raise exceptions.MethodNotFound("Method '%s' not found in "
                "interface %s" % (request.method, self.name))

        return method_info.call(self, request)


class Method(object):
    """Class for holding wrapped method.

    Should not be created directly, only using :func:`pycom.method`.
    Available through `__method__` attribute of any remote-invokable method.

    .. attribute:: wrapped

       Link to original method.

    .. attribute:: name

       Method name.

    .. attribute:: prehooks
    .. attribute:: posthooks

       Lists of hooks that should be executed for pre- and post- processing
       incoming and outgoing data. Hook is a callable with the following
       signature:

        .. function:: hook(iface, method, data)

           .. attribute:: iface
              :noindex:

              :class:`pycom.interfaces.Interface` object.

           .. attribute:: method
              :noindex:

              :class:`pycom.interfaces.Method` object.

           .. attribute:: data
              :noindex:

              Data to be processed (:class:`pycom.Request` for prehooks,
              :class:`pycom.Response` for posthooks).

       Example from tests::

        import pycom

        def setup_my_hook(meth):
            def my_hook(iface, method, data):
                pass  # ...
            meth.__method__.prehooks.append(my_hook)
            return meth

        @pycom.interface("...")
        class InterfaceWithMethods(pycom.Service):

            @setup_my_hook
            @pycom.method("...")
            def method1(self, request):
                pass  # ...

       Do NOT try to use things like ``functools.wraps`` and
       standard decorators on PyCOM methods, they behave in a different way.

    .. attribute:: required_arguments
    .. attribute:: optional_arguments

        List of strings - required and optional arguments declaration.
        If present, input will be checked, :exc:`pycom.BadRequest` raised
        when necessary. Required arguments are passed as positional,
        optional - as keyword.

    .. attribute:: results

        List of strings - results declaration.
        If present, output will be checked, resulting tuple will be unpacked,
        and JSON object will be sent back.

    """

    __slots__ = ("wrapped", "name", "prehooks", "posthooks",
        "required_arguments", "optional_arguments", "results")

    def __init__(self, wrapped, name, results=()):
        """C-tor. Never call it directly, use pycom.method decorator."""
        self.wrapped = wrapped
        self.name = name
        self.prehooks = []
        self.posthooks = []
        self.results = results

        info = inspect.getargspec(wrapped)
        if info.defaults:
            self.required_arguments = info.args[2:-len(info.defaults)]
            self.optional_arguments = info.args[-len(info.defaults):]
        else:
            self.required_arguments = info.args[2:]
            self.optional_arguments = ()

    def post_configure(self, owner_iface):
        """Called once *owner_iface* is fully configured."""

    def call(self, iface, request):
        """Call this method with given :class:`pycom.protocol.Request`.

        *iface* should be :class:`pycom.interfaces.Interface` object.

        Returns :class:`pycom.Response` object.

        """
        if self.required_arguments or self.optional_arguments:
            if request.args is None:
                request.args = {}
            if not isinstance(request.args, dict):
                raise exceptions.BadRequest("Expected dictionary as argument "
                    "for %s.%s" % (iface.name, self.name))

        for hook in self.prehooks:
            request = hook(iface, self, request)

        args = tuple(_fetch_argument(request.args, name, iface.name, self.name)
            for name in self.required_arguments)
        kwargs = dict((name, request.args[name])
            for name in self.optional_arguments
            if name in request.args)

        response = self.wrapped(iface.instance, request, *args, **kwargs)
        if not isinstance(response, base.Response):
            response = request.response(response)

        if len(self.results) == 1:
            response.result = {self.results[0]: response.result}
        elif len(self.results) > 1:
            if not isinstance(response.result, tuple) \
                    or len(response.result) != len(self.results):
                raise RuntimeError(
                    "Method %s.%s is expected to return a tuple of %d items" %
                    (iface.name, self.name, len(self.results)))
            response.result = dict(zip(self.results, response.result))

        for hook in self.posthooks:
            response = hook(iface, self, response)

        return response


# Private


def _fetch_argument(args, name, method_name, iface_name):
    """Fetch given argument from args."""
    try:
        return args[name]
    except KeyError:
        raise exceptions.BadRequest("Argument '%s' is required for %s.%s" %
            (name, method_name, iface_name))
