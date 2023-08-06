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

"""Helpers to ease creating services."""

from six import iteritems, string_types

from . import constants, interfaces


def interface(name, **kwargs):
    """Decorator for interface *name*.

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service): pass

    Deriving from :class:`pycom.Service` is completely optional,
    but this base class provides support for introspecting your methods.

    Interfaces are stateless by default, you can make them steteful by
    using ``stateful`` argument::

        import pycom

        @pycom.interface("com.example.interface.foo", stateful=True)
        class ClassProvidingInterface(pycom.Service): pass

    Argument ``authentication`` overrides global authentication policy
    and can take two string values: ``"required"`` and ``"never"``.

    """
    def _wrapper(wrapped):
        """This callable temporary wraps method."""
        if not isinstance(getattr(wrapped, "introspection_data", {}), dict):
            raise TypeError("introspection_data should be a dict, if present")

        wrapped.__interface__ = interfaces.Interface(wrapped, name, **kwargs)
        return wrapped

    return _wrapper


def method(name=None, body=None, method_factory=None, results=(),
        attachments=(None, None)):
    """Decorator for method *name*.

    Method should take at least one positional argument: *request*,
    which is an object of type :class:`zerojson.Request`.

    Method should return either JSON-serializable entity,
    or result of `request.response()` call
    (see :meth:`zerojson.Request.response`),
    i.e. :class:`zerojson.Response` object.

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method
            def method_name(self, request): print request.args

    If *body* is present, this function does not act as a decorator,
    but directly return appropriate object for
    :meth:`pycom.interfaces.Interface.register_method`.
    Here is a useful snippet for adding method in runtime::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service): pass

        def method_body(self, request): pass

        ClassProvidingInterface.__interface__.register_method(
            pycom.method("method_name", body=method_body))

    *method_factory* is used internaly for overriding method class
    (default is :class:`pycom.interfaces.Method`).

    PyCOM will do it's best to detect any additional arguments that
    your method can take, e.g. you can write::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method
            def method_name(self, request, arg1, arg2, arg3=None):
                print arg1, arg2, arg3

    PyCOM will use Python's introspection features to guess that
    ``arg1`` and ``arg2`` are required arguments, ``arg3`` is an optional one.
    :exc:`pycom.BadRequest` will be raised, if required argument is missing,
    or input is not a JSON object.

    However, PyCOM cannot guess whether you have one result or several,
    and what are their names. You can give it a hint by filling *results*
    tuple with names of the resulting arguments, e.g.::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method(results=("res1", "res2"))
            def method_name(self, request, arg1, arg2, arg3=None):
                return arg2, arg3

    If you are going to use introspection (and e.g.
    :class:`pycom.ProxyComponent`) with the method, you may also fill
    *attachments* argument with a tuple of 2 elements: names for
    incoming and outgoing attachment parameters or ``None``'s::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method(attachments=("blob", None))
            def method_name(self, request, blob):
                return blob.decode("utf-8")

    Note that incoming attachment turned into an argument to the method.
    For outgoing attachment you should add outgoing attachment name to
    results list and return the attachment in a result tuple::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method(attachments=(None, "blob"), results=("orig", "blob"))
            def method_name(self, request, string):
                return string, string.encode("utf-8")

    Finally, you can explicitly state remote method name::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method("method_name")
            def method_impl(self, request): print request.args

    If interface is stateful (see :func:`pycom.interface`), ``request``
    will have ``session`` attribute with dictionary.
    You can store arbitrary data there and
    it will be persisted across requests.

    """
    method_factory = method_factory or interfaces.Method
    if body is None:
        if name is not None and not isinstance(name, string_types):
            name, wrapped = name.__name__, name
            wrapped.__method__ = method_factory(wrapped, name)
            return wrapped

        def _wrapper(wrapped):
            """This callable temporary wraps method."""
            new_name = name if name is not None else wrapped.__name__
            wrapped.__method__ = method_factory(wrapped, new_name, results,
                attachments)
            return wrapped

        return _wrapper
    else:
        return method_factory(body, name)


# pylint: disable-msg=C0322,W0613

class Service(object):
    """Helpful base class (or mix-in) for services.

    Adds introspection support via ``introspect`` remote call.

    Imagine a service::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):
            "My Demo Service"

            introspection_data = {
                "com.example.interface.foo.x": None
            }

            @pycom.method(results=("res1", "res2"))
            def method_name(self, request, arg1, arg2, arg3=None):
                "My Demo Method"
                return arg2, arg3

    This call will return the following JSON::

        {
          "name": "com.example.interface.foo",
          "methods": {
            "introspect": {
              "required_arguments": [],
              "optional_arguments": [],
              "results": ["name", "methods", "docstring", "data"],
              "docstring": "Provides introspection information for a service.",
              "attachments": {
                "incoming": None,
                "outgoing": None
              }
            },
            "method_name": {
              "required_arguments": ["arg1", "arg2"],
              "optional_arguments": ["arg3"],
              "results": ["res1", "res2"],
              "docstring": "My Demo Method",
              "attachments": {
                "incoming": None,
                "outgoing": None
              }
            }
          },
          "docstring": "My Demo Service",
          "data": {
            "com.example.interface.foo.x": None
          }
        }

    Note that ``introspect`` method is also included.

    ``introspection_data`` (if present) should be a dictionary.

    """

    __interface__ = None

    @method(constants.GENERIC_METHOD_INTROSPECT,
        results=("name", "methods", "docstring", "data"))
    def introspect(self, request):
        """Provides introspection information for a service."""
        methods = dict((name, {
                "required_arguments": list(info.required_arguments),
                "optional_arguments": list(info.optional_arguments),
                "results": list(info.results),
                "docstring": info.wrapped.__doc__,
                "attachments": dict(
                    incoming=info.attachments[0],
                    outgoing=info.attachments[1]
                )
            })
            for name, info in iteritems(self.__interface__.methods)
        )
        return (self.__interface__.name, methods, self.__doc__,
            getattr(self, "introspection_data", {}))

# pylint: enable-msg=C0322,W0613
