Public API Reference
=====================

Writing services
-----------------------------

.. autofunction:: pycom.interface

.. autofunction:: pycom.method

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
   *timeout* is in milliseconds.

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
