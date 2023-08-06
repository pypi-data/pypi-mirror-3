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

from six import iteritems

from . import constants, interfaces


def interface(name):
    """Decorator for interface *name*.

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service): pass

    Deriving from :class:`pycom.Service` is completely optional,
    but this base class provides support for introspecting your methods.

    """
    def _wrapper(wrapped):  # pylint: disable-msg=C0111
        wrapped.__interface__ = interfaces.Interface(wrapped, name)
        return wrapped

    return _wrapper


def method(name, body=None, method_factory=None, results=()):
    """Decorator for method *name*.

    Method should take at least one positional argument: *request*,
    which is an object of type :class:`pycom.Request`.

    Method should return either JSON-serializable entity,
    or result of `request.response()` call
    (see :meth:`pycom.Request.response`), i.e. :class:`pycom.Response` object.

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(pycom.Service):

            @pycom.method("method_name")
            def my_method(self, request): print request.args

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

            @pycom.method("method_name")
            def my_method(self, request, arg1, arg2, arg3=None):
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

            @pycom.method("method_name", results=("res1", "res2"))
            def my_method(self, request, arg1, arg2, arg3=None):
                return arg2, arg3

    """
    method_factory = method_factory or interfaces.Method
    if body is None:
        def _wrapper(wrapped):  # pylint: disable-msg=C0111
            wrapped.__method__ = method_factory(wrapped, name, results)
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

            @pycom.method("method_name", results=("res1", "res2"))
            def my_method(self, request, arg1, arg2, arg3=None):
                "My Demo Method"
                return arg2, arg3

    This call will return the following JSON::

        {
          "name": "com.example.interface.foo",
          "methods": {
            "introspect": {
              "required_arguments": [],
              "optional_arguments": [],
              "results": ["name", "methods", "docstring"],
              "docstring": "Provides introspection information for a service."
            },
            "method_name": {
              "required_arguments": ["arg1", "arg2"],
              "optional_arguments": ["arg3"],
              "results": ["res1", "res2"],
              "docstring": "My Demo Method"
            }
          },
          "docstring": "My Demo Service"
        }

    Note that ``introspect`` method is also included.

    """

    __interface__ = None

    @method(constants.GENERIC_METHOD_INTROSPECT,
        results=("name", "methods", "docstring"))
    def introspect(self, request):
        """Provides introspection information for a service."""
        methods = dict((name, {
                "required_arguments": list(info.required_arguments),
                "optional_arguments": list(info.optional_arguments),
                "results": list(info.results),
                "docstring": info.wrapped.__doc__
            })
            for name, info in iteritems(self.__interface__.methods)
        )
        return self.__interface__.name, methods, self.__doc__

# pylint: enable-msg=C0322,W0613
