Configuration
==============

Service configuration is stored in a JSON file.
There is no standard location now, every service should
set it manually using :func:`pycom.configure`. Nameserver
configuration is in: `$PREFIX/share/pycom/ns.conf`.

.. note::

    `easy_install` overrides this directory with something complicated, e.g.
    `$PREFIX/lib/python2.7/site-packages/pycom-0.1-py2.7.egg/share/pycom/`.
    We are investigating this issue. Use `pip` when possible.

Configuration top-level objects should contain the following properties:

.. data:: address

   IP and port to listen on. This address will be reported to the
   nameserver on initialization and should be reachable from other
   services in your system.

   Address is in 0MQ format and looks like: `tcp://host:port`.

    .. note::

       Do not set address to `tcp://127.0.0.1:xxxx` unless all your
       services run on localhost.

.. data:: service

   Service name (e.g. `/com/example/service/name`).
   Must be unique in your system.

For all services except nameserver you'll have to set also:

.. data:: nameserver

   0MQ address of the nameserver (e.g. `tcp://127.0.0.1:2012`).
   You can skip this property only if you have nameserver built into
   your service, e.g.::

        import pycom
        import pycom.apps.nameserver

        # Your service goes here...

   As of PyCOM 0.1, you still need external address for such services.
