Public API Reference
=====================

This is public Python API for both server and client side of PyCOM.
Private API bits are not stated here. Still, you can find their
documentation in the docstrings.

PyCOM uses standard `logging` module to do it's logging, logger name being
`pycom`.

If you are interested in C++ API, have a look at this page:
https://bitbucket.org/divius/libpycom

Writing services
-----------------------------

.. autofunction:: pycom.interface

   Additional attribute is defined on class with interface:

   .. attribute:: __interface__

      Interface metainformation for this class -
      instance of :class:`pycom.interfaces.Interface`.

.. autofunction:: pycom.method

   .. note::

      As of PyCOM 0.3, methods cannot be added at run time, only on class
      declaration.

.. autofunction:: pycom.main

.. autofunction:: pycom.ioloop

.. autoclass:: pycom.Request

Invoking services
------------------

.. autofunction:: pycom.nameserver

.. autofunction:: pycom.locate

Both of these functions return special objects called *components*,
each of them implementing interface:

    .. autoclass:: pycom.BaseComponent
       :members:

Both of these functions will raise :exc:`pycom.ServiceNotFound`
if service is unknown or unreachable.

Example client code::

    ns = pycom.locate("org.pycom.nameserver")
    for service in ns.invoke("list_services"):
        print(service["service"], service["interface"])

or (the same, but faster) ::

    ns = pycom.nameserver()
    for service in ns.invoke("list_services"):
        print(service["service"], service["interface"])

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

.. autoexception:: pycom.RemoteError
