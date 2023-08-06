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

Here we use classes from ZeroJSON implementation package:

.. autoclass:: zerojson.Request
   :members:
   :exclude-members: initialize_session

   .. method:: context()

      Generates preconfigured :class:`pycom.ProxyContext`. If authentication
      token is provided by client, it is also set on a context.

      .. note:: This method is set by PyCOM and is absent in pure ZeroJSON.

.. autoclass:: zerojson.Response
   :members:

.. autoclass:: zerojson.Session
   :members:

There is a way to write asynchronous services with PyCOM/ZeroJSON:

.. autoclass:: zerojson.Future
   :members:
   :exclude-members: add_callback, prepare

Return ``Future`` object from your method instead of a real response
and do not forget to call one of it's methods later.

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

   All members are the same as in :class:`pycom.Context`, except:

.. autoclass:: pycom.ProxyComponent
   :members:

.. note::

    Never store components for a long time! Any component is bound to the
    specific address, but your services can change their location.
    Furthermore, a session bound to your component can expire and you'll
    get :exc:`pycom.SessionExpired`.

Altering configuration
-----------------------

.. autofunction:: pycom.configure

.. data:: pycom.configuration

   Dictionary with current configuration. Should not be altered directly!

Exceptions
-----------

Following exceptions can be raised on client side or on remote side:

.. autoexception:: pycom.RemoteError

.. autoexception:: pycom.ServiceNotFound

.. autoexception:: pycom.MethodNotFound

.. autoexception:: pycom.BadRequest

.. autoexception:: pycom.AccessDenied

.. autoexception:: pycom.SessionExpired

Following exceptions can be raised on client side only:

.. autoexception:: pycom.ServiceNotAvailable

.. autoexception:: pycom.ConfigurationError

Note that all but the last exceptions are in fact
defined in `zerojson` package.
