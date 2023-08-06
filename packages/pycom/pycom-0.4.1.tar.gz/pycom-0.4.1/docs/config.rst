Running services
=================

Configuration
--------------

Service configuration is stored in a JSON file.
There is no standard location now, every service should
set it manually using :func:`pycom.configure`. Nameserver
configuration is in: `$PREFIX/share/pycom/ns.conf`.

.. note::

    `easy_install` overrides this directory with something complicated, e.g.
    `$PREFIX/lib/python2.7/site-packages/pycom-0.4.0-py2.7.egg/share/pycom/`.
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
   Must be unique in your system. If service is not set, it is generated, e.g.
   `/auto/b42712345bea11e191c9dca97122e60b`.

For all services except nameserver you'll have to set also:

.. data:: nameserver

   0MQ address of the nameserver (e.g. `tcp://127.0.0.1:2012`).
   You can skip this property only if you have nameserver built into
   your service, e.g.::

        import pycom
        import pycom.apps.nameserver

        # Your service goes here...

   As of PyCOM 0.4, you still need external address for such services.

Command-line Interface
-----------------------

For simple cases you can omit creating a configuration file and use
command-line interface to set required parameters.

Base command line for starting any number of services is::

    python -m pycom [flags] path.to.service1 [path.to.service2 ...]

where

.. data:: path.to.service
    :noindex:

    Full qualified module name[s] for service[s] to run

.. data:: -s *service-name*
    :noindex:

    This flag sets service name

.. data:: -a *address*
    :noindex:

    This flags sets address to listen on

.. data:: -n *address*
    :noindex:

    This flag sets nameserver address

.. data:: -v
    :noindex:

    This flag increase verbosity

Example for NameServer::

    python -m pycom -a tcp://127.0.0.1:2012 -s /org/pycom/nameserver pycom.apps.nameserver

and for some other service::

    python -m pycom -a tcp://127.0.0.1:2013 -s /mypkg/svc1 -n tcp://127.0.0.1:2012 \
        mypkg.svc1.iface1 mypkg.svc1.iface
