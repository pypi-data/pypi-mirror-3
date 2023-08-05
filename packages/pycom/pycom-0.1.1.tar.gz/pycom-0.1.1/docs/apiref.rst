Public API Reference
=====================

This is public Python API for both server and client side of PyCOM.
Private API bits are not stated here. Still, you can find their
documentation in the docstrings.

If you are interested in C++ API, have a look at this page:
https://bitbucket.org/divius/libpycom

Writing services
-----------------------------

.. autofunction:: pycom.interface

   Additional attribute is defined on class with interface:

   .. attribute:: __interface__

      Interface metainformation for this class. In turn, this object has three
      read-only attributes:

      .. attribute:: wrapped

         Link to owner class.

      .. attribute:: name

         Interface name.

      .. attribute:: methods

         Dictionary of methods for this class, keys being method names.

.. autofunction:: pycom.method

   .. note::

      As of PyCOM 0.1, methods cannot be added at run time, only on class
      declaration.

.. autofunction:: pycom.main

.. autofunction:: pycom.ioloop

Invoking services
------------------

.. autofunction:: pycom.nameserver

.. autofunction:: pycom.locate

Both of these functions return special objects called *invokers*.
Each invoker has at least one method:

.. method:: invoke(method_name, args=None, timeout=None)

   This method calls *method_name* on a remote service, passing *args*
   as argument. *args* should be anything JSON-serializable.

   *timeout* can be used to prevent *invoke* from hanging forever.
   *timeout* is in milliseconds and defaults to 5000.

   Raises :exc:`pycom.MethodNotFound` if service doesn't provide
   method *method_name*. Raises :exc:`pycom.ServiceNotAvailable`
   if service cannot be reached during request.

Both of these functions will raise :exc:`pycom.ServiceNotFound`
if service is unknown or unreachable.

Example client code::

    ns = pycom.locate("org.pycom.nameserver")
    for service in ns.invoke("list_services"):
        print(service["service"], service["interface"])

or (the same but faster) ::

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
