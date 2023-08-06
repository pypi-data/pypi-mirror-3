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

"""Checks for services."""

import pycom


try:
    callable
except NameError:  # pragma: no cover
    # py3k < 3.2 sucks
    callable = lambda x: hasattr(x, '__call__')  # pylint: disable-msg=W0622


def check_argument(name, valid_types=None, validator=None,
        error_message=None):
    """A decorator for checking types of incoming arguments.

    *name* is a name of argument to check.

    *valid_types* is a tuple with allowed types or just a single type.

    *validator* is a callable that takes 2 arguments
      (argument name and argument value),
      positive result designate valid value, negative result or raising
      `TypeError` or `ValueError` designate invalid value
      (error message is taken from the exception).

    *error_message* overrides default error message.

    Example::

        import pycom
        from pycom.ext import checks

        @pycom.interface("com.example.interface.foo")
        class SimpleInterface(pycom.Service):

            @checks.check_argument("arg1", valid_types=str,
                validator=lambda name, value: len(value) > 0)
            @checks.check_argument("arg2", valid_types=(int, type(None)),
                validator=(lambda name, value: value is None or value > 0),
                error_mesage="Required positive integer or None for arg2")
            @pycom.method
            def my_method(self, request, arg1, arg2): pass

    This decorator can be used any number of times, but should be placed before
    :func:`pycom.method`.

    :exc:`pycom.BadRequest` is raised on failed checks.

    """
    assert valid_types is None or isinstance(valid_types, (tuple, type))
    assert validator is None or callable(validator)

    def _checker(iface, method, request):
        """This prehook checks incoming data."""
        if name not in request.args:
            # We do NOT check presence!
            return request

        value = request.args[name]
        try:
            if valid_types is not None:
                if not isinstance(value, valid_types):
                    raise TypeError(
                        "Invalid type for argument '%s' of '%s.%s', "
                        "expected '%s', got '%s'" % (
                            name, iface.name, method.name,
                            valid_types, type(value)
                        ))
            if validator is not None:
                if not validator(name, value):
                    raise ValueError(
                        "Validation failed for argument '%s' of '%s.%s'" % (
                            name, iface.name, method.name
                        ))
        except (ValueError, TypeError) as err:
            if error_message is not None:
                raise pycom.BadRequest(error_message)
            else:
                raise pycom.BadRequest(str(err))

        return request

    def _wrapper(wrapped):
        """This wrapper is called on method creation by decorator."""
        wrapped.__method__.prehooks.append(_checker)
        return wrapped

    return _wrapper
