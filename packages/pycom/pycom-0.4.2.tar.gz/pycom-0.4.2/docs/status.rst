Project Status
===============

Known Issues
-------------

Benchmarks
-----------

Here are some benchmarks of PyCOM 0.4.2 in the local network (100Mbps).

NameServer was running on::

    Software: Linux 2.4.32 i386, Python 2.7.2, PyZMQ 2.1.11
    Hardware: VirtualBox 4.1.8 (without additions)
    Host: Ubuntu 12.04 x86_64

Remote client was running on::

    Software: Ubuntu 11.10 x86_64, Python 2.7.2, Python 3.2.2, PyZMQ 2.1.11
    Hardware: SAMSUNG 350 U2A notebook

Two command were executed::

    $ ./python -m timeit \
        -s "import pycom; ctx = pycom.ProxyContext(nameserver='tcp://192.168.10.13:2012')" \
        "ctx.nameserver().stat()"
    $ ./python -m timeit \
        -s "import pycom; ctx = pycom.ProxyContext(nameserver='tcp://192.168.10.13:2012')" \
        "ctx.locate('org.pycom.nameserver').stat()"

Results for remote client (Python 2.7.2)::

    1: 100 loops, best of 3: 4.33 msec per loop
    2: 100 loops, best of 3: 9.45 msec per loop

Results for remote client (Python 3.2.2)::

    1: 100 loops, best of 3: 4.06 msec per loop
    2: 100 loops, best of 3: 9.58 msec per loop

Local client::

    1: 1000 loops, best of 3: 1.17 msec per loop
    2: 100 loops, best of 3: 1.99 msec per loop

Localhost-only setup (NameServer address is ``tcp://127.0.0.1:2012``)::

    1: 1000 loops, best of 3: 1.16 msec per loop
    2: 100 loops, best of 3: 2.09 msec per loop

Localhost-only setup (NameServer address is ``ipc:///tmp/test-pycom``)::

    1: 1000 loops, best of 3: 1.15 msec per loop
    2: 100 loops, best of 3: 1.96 msec per loop

Thus, for LAN setups average rate is about 230 simple requests per second
or 100 lookup-request pairs per second.

For localhost setups average rate is about 850 simple requests per second
or 480 lookup-request pairs per second.

Roadmap
---------

0.5 series
~~~~~~~~~~~

- Introduce hooks for Context object (``prehooks`` and ``posthooks``)
- Provide arbitrary data for service via name server
  (via ``registration_data`` argument for ``@pycom.interface``)
- Authentication support via special service with
  ``org.pycom.authenticator`` interface,
  ``@pycom.ext.auth.check_authentication`` server-side decorator and
  ``pycom.ext.auth.authenticate(context, user, **credentials)``
  client-side function.
- Introduce asynchronous client API (using ``pycom.ioloop()``) via
  ``pycom.ext.async.AsyncContext`` class

0.6 series
~~~~~~~~~~~

- Switch to new protocol (see appropriate section)
- Name servers replication (with and without *domains*)
- Messaging middleware system on top of PyCOM via special service with
  ``org.pycom.messaging.queue``, ``org.pycom.messaging.message`` interfaces
  and ``@pycom.ext.messaging.listener``, ``@pycom.ext.messaging.handler``
  decorators
- Local peer optimization (switch to ipc:// sockets, transfer attachments
  via local files)

1.0.0
~~~~~~

- C++ client stubs compiler
- Stable release with bug fixes!

1.1.0
~~~~~~

- Service pool management software
- Reliable delayed calls support on top of messaging middleware
- Authentication of services on registering
- *Workflow* extension for defining business processes
- ... more coming later ...
- Stable release with bug fixes!
