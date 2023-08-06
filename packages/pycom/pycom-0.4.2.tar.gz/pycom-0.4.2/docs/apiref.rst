Public API Reference
=====================

This is public Python API for both server and client side of PyCOM.
Private API bits are not stated here. Still, you can find their
documentation in the docstrings.

PyCOM uses standard `logging` module to do it's logging, logger name being
`pycom` (or use :func:`pycom.utils.logger`).

If you are interested in C++ API, have a look at this page:
https://bitbucket.org/divius/libpycom

Writing services
-----------------------------

.. autofunction:: pycom.interface

   Additional attribute is defined on class with interface:

   .. attribute:: __interface__

      Interface metainformation for this class -
      instance of :class:`pycom.interfaces.Interface`.

.. autoclass:: pycom.Service
   :members:

.. autofunction:: pycom.method

For strict type checks you can use an extensions
(available in module `pycom.ext.checks`):

.. autofunction:: pycom.ext.checks.check_argument

.. autofunction:: pycom.main

.. autoclass:: pycom.Request
   :members:

.. autoclass:: pycom.Response
   :members:

Invoking services
------------------

.. autoclass:: pycom.Context
   :members:

Both of these functions return special objects called *components*,
each of them implementing interface:

    .. autoclass:: pycom.BaseComponent
       :members:

Both of these functions will raise :exc:`pycom.ServiceNotFound`
if service is unknown or unreachable.

Example client code::

    ctx = pycom.Context(nameserver="tcp://...")
    ns = ctx.locate("org.pycom.nameserver")
    for service in ns.invoke("list_services"):
        print(service["service"], service["interface"])

or (the same, but faster and cleaner) ::

    ctx = pycom.Context(nameserver="tcp://...")
    ns = ctx.nameserver()
    for service in ns.invoke("list_services"):
        print(service["service"], service["interface"])

or (the same, but with correct closing) ::

    ctx = pycom.Context(nameserver="tcp://...")
    with ctx.nameserver() as ns:
        for service in ns.invoke("list_services"):
            print(service["service"], service["interface"])

A more convenient way is to use proxying context and components:

.. autoclass:: pycom.ProxyContext
   :members:

.. autoclass:: pycom.ProxyComponent
   :members:

This is an underlying implementation for all components:

.. autoclass:: pycom.RemoteComponent
   :members:

Altering configuration
-----------------------

.. autofunction:: pycom.configure

.. data:: pycom.configuration

   Dictionary with current configuration. Should not be altered directly!

Exceptions
-----------

Following exceptions can be raised on client side:

.. autoexception:: pycom.Error

.. autoexception:: pycom.ConfigurationError

.. autoexception:: pycom.ServiceNotFound

.. autoexception:: pycom.ServiceNotAvailable

.. autoexception:: pycom.MethodNotFound

.. autoexception:: pycom.BadRequest

.. autoexception:: pycom.AccessDenied

.. autoexception:: pycom.RemoteError
