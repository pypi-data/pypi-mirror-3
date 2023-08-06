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

from six import iteritems

from . import base, exceptions


def interface(name):
    """Decorator for interface *name*.

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(object): pass

    """
    def _wrapper(wrapped):  # pylint: disable-msg=C0111
        wrapped.__interface__ = Interface(wrapped, name)
        return wrapped

    return _wrapper


def method(name, body=None):
    """Decorator for method *name*.

    Method should take at least one positional argument: *request*,
    which is an object of type :class:`pycom.Request`.

    Method should return either JSON-serializable entity,
    or result of `request.response()` call
    (see :meth:`pycom.Request.response`).

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(object):

            @pycom.method("method_name")
            def my_method(self, request): print request.args

    If *body* is present, this function does not act as a decorator,
    but directly return appropriate object for
    :meth:`pycom.interfaces.Interface.register_method`.
    Here is a useful snippet for adding method in runtime::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(object): pass

        def method_body(self, request): pass

        ClassProvidingInterface.__interface__.register_method(
            pycom.method("method_name", body=method_body))

    """
    if body is None:
        def _wrapper(wrapped):  # pylint: disable-msg=C0111
            wrapped.__method__ = Method(wrapped, name)
            return wrapped

        return _wrapper
    else:
        return Method(body, name)


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

        for key, value in iteritems(wrapped.__dict__):
            method_info = getattr(value, "__method__", None)
            if method_info is None:
                continue

            self.register_method(method_info)

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
            base.Request(self.name, method_name, base.Session(None), args))

    def invoke_with_request(self, request):
        """Invoke method using given request object."""
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

              Data to be pre- or post- processed.

       Example from tests::

        import pycom

        def setup_my_hook(meth):
            def my_hook(iface, method, data):
                pass  # ...
            meth.__method__.prehooks.append(my_hook)
            return meth

        @pycom.interface("...")
        class InterfaceWithMethods(object):

            @setup_my_hook
            @pycom.method("...")
            def method1(self, request):
                pass  # ...

    """

    __slots__ = ("wrapped", "name", "prehooks", "posthooks")

    def __init__(self, wrapped, name):
        """C-tor. Never call it directly, use pycom.method decorator."""
        self.wrapped = wrapped
        self.name = name
        self.prehooks = []
        self.posthooks = []

    def call(self, iface, request):
        """Call this method with given :class:`pycom.protocol.Request`.

        *iface* should be :class:`pycom.interfaces.Interface` object.

        """
        for hook in self.prehooks:
            request.args = hook(iface, self, request.args)

        result = self.wrapped(iface.instance, request)

        for hook in self.posthooks:
            result = hook(iface, self, result)

        return result
