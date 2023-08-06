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

import zerojson

from . import base, constants, proxy


class Interface(base.BaseComponent):
    """Internal object, representing interface.

    Should not be created directly, only using :func:`pycom.interface`.
    Available through :attr:`__interface__` attribute
    of objects with interface (and their classes).

    Inherits :class:`pycom.BaseComponent`, allows directly calling methods.

    .. attribute:: instance

       Stored owner class instance.

    .. attribute:: methods

       Dictionary of methods for this class, keys being method names,
       value being objects of type :class:`pycom.interfaces.Method`.

    .. attribute:: stateful

       Boolean value, whether this interface is stateful or not.

    .. attribute:: authentication

       Authentication policy - see :func:`pycom.interface`.

    """

    __slots__ = ("instance", "methods", "stateful", "authentication")

    def __init__(self, wrapped, name, stateful=False, authentication=None):
        """C-tor. Never call it directly, use pycom.interface decorator."""
        super(Interface, self).__init__(name)

        if name in base.interface_registry and not \
                isinstance(base.interface_registry[name], wrapped):
            raise RuntimeError("Interface %s is already registered "
                "for object %s" % (name, repr(base.interface_registry[name])))

        self.instance = wrapped()
        self.methods = {}
        self.stateful = stateful
        self.authentication = authentication

        for key in dir(wrapped):
            method_info = getattr(getattr(wrapped, key), "__method__", None)
            if method_info is None:
                continue

            self.register_method(method_info)

        for method_info in itervalues(self.methods):
            method_info.post_configure(self)

        base.interface_registry[name] = self.instance

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

    def invoke_with_request(self, request,
            timeout=None):
        """Invoke method using given request object.

        *timeout* is ignored here.

        Returns :class:`zerojson.Response` object.

        """
        try:
            method_info = self.methods[request.method]
        except KeyError:
            raise zerojson.MethodNotFound("Method '%s' not found in "
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

              Data to be processed (:class:`zerojson.Request` for prehooks,
              :class:`zerojson.Response` for posthooks).

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
            @pycom.method
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

    .. attribute:: attachments

        A tuple of 2 strings: names for incoming and outgoing attachment
        parameters. Mostly used in introspection and
        :class:`pycom.ProxyComponent`. Defaults to ``(None, None)``.

    """

    __slots__ = ("wrapped", "name", "prehooks", "posthooks",
        "required_arguments", "optional_arguments", "results", "attachments")

    def __init__(self, wrapped, name, results=(), attachments=(None, None)):
        """C-tor. Never call it directly, use pycom.method decorator."""
        self.wrapped = wrapped
        self.name = name
        self.prehooks = []
        self.posthooks = []
        self.results = results
        self.attachments = attachments

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
        """Call this method with given :class:`pycom.zerojson.Request`.

        *iface* should be :class:`pycom.interfaces.Interface` object.

        Returns :class:`zerojson.Response` object.

        """
        # Client context

        token = request.extensions.get(constants.AUTH_EXTENSION)

        def _context_builder():
            """Utility to generate new context."""
            ctx = proxy.ProxyContext()
            if token is not None:
                ctx.authenticate(token=token)
            return ctx

        request.context = _context_builder

        if _auth_policy(iface) == "required":
            if request.context().user_info() is None:
                raise zerojson.AccessDenied("Authentication required")

        # Prepare arguments

        if self.required_arguments or self.optional_arguments:
            if request.args is None:
                request.args = {}
            if not isinstance(request.args, dict):
                raise zerojson.BadRequest("Expected dictionary as argument "
                    "for %s.%s" % (iface.name, self.name))

        # Run prehooks

        for hook in self.prehooks:
            request = hook(iface, self, request)

        # Finish processing arguments

        args = tuple(_fetch_argument(request, name, iface.name, self.name,
                self.attachments[0])
            for name in self.required_arguments)
        kwargs = dict((name, request.args[name])
            for name in self.optional_arguments
            if name in request.args)

        # Invoke method

        response = self.wrapped(iface.instance, request, *args, **kwargs)

        # Future objects support

        if isinstance(response, zerojson.Future):
            response.add_callback(self._after_call, iface)
            return response

        # Response post-processing

        if not isinstance(response, zerojson.Response):
            response = request.response(response)

        return self._after_call(iface, response)

    # Private

    def _after_call(self, iface, response):
        """Routine to run after call."""
        if self.results:
            if len(self.results) == 1:
                response.result = (response.result,)

            if not isinstance(response.result, tuple) \
                    or len(response.result) != len(self.results):
                raise RuntimeError(
                    "Method %s.%s is expected to return a tuple of %d items" %
                    (iface.name, self.name, len(self.results)))
            response.result = dict(zip(self.results, response.result))

            att_name = self.attachments[1]
            if att_name in response.result:
                response.attachment = response.result[att_name]
                del response.result[att_name]

        for hook in self.posthooks:
            response = hook(iface, self, response)

        return response


# Private


def _auth_policy(iface):
    """Get authentication policy for an interfaces."""
    return iface.authentication or \
        base.configuration.get("authentication", {}).get("policy")


def _fetch_argument(request, name, method_name, iface_name, att_name):
    """Fetch given argument from args."""
    if name == att_name:
        return request.attachment

    try:
        return request.args[name]
    except KeyError:
        raise zerojson.BadRequest("Argument '%s' is required for %s.%s" %
            (name, method_name, iface_name))
