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

import collections

from six import iteritems


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


def method(name):
    """Decorator for method *name*.

    Method should take at least one positional argument: *request*,
    which is an object with the following attributes:

    .. attribute:: interface

       Current interface name

    .. attribute:: method

       Current method name

    .. attribute:: args

       Arguments passed by client side as Python object

    Example::

        import pycom

        @pycom.interface("com.example.interface.foo")
        class ClassProvidingInterface(object):

            @pycom.method("method_name")
            def my_method(self, request): print request.args

    """
    def _wrapper(wrapped):  # pylint: disable-msg=C0111
        return _Method(wrapped, name)

    return _wrapper


registry = {}


class Interface(object):
    """Internal interface object."""

    __slots__ = ("wrapped", "name", "methods")

    def __init__(self, wrapped, name):
        """C-tor. Never call it directly, use pycom.interface decorator."""
        if name in registry and registry[name] is not wrapped:
            raise RuntimeError("Interface %s is already registered "
                "for object %s" % (name, repr(registry[name])))

        self.name = name
        self.wrapped = wrapped
        self.methods = {}

        # Operate on a copy of __dict__ as we change original on fly
        for key, value in iteritems(wrapped.__dict__.copy()):
            if not isinstance(value, _Method):
                continue

            # Register method
            self._register_method(value.wrapped, value.name)

            # And restore actual method
            setattr(wrapped, key, value.wrapped)

        registry[name] = wrapped

    # Private

    def _register_method(self, func, func_name):
        """Register method under given name."""
        if func_name in self.methods and self.methods[func_name] is not func:
            raise RuntimeError("Function %s is already registered "
                "for interface %s" % (func_name, self.name))

        self.methods[func_name] = func


# Private API


class _Method(collections.namedtuple("_Method", "wrapped name")):
    """Class for temporary holding wrapped method."""
