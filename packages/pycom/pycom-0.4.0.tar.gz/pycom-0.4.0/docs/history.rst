Release History
================

0.4 series
-----------

v0.4.0
+++++++

Released on `Mon Feb 20 18:03:39 UTC 2012`.

- Method :meth:`pycom.Request.response`
- Respect `PYCOM_LOGGING_LEVEL` environment variable
- :func:`pycom.method` decorator got *body* argument
- More error checks in server implementation; test coverage is 100% now
- Refactored internals, introduced `pycom.zerojson` package
- Drafts for future protocol and ``PREPARE`` command
- Command-line option ``--nameserver``/``-n``
- Demonstration service ``pycom.apps.demo`` with interface ``org.pycom.demo``
- Service name can be automatically generated now

Old releases
-------------

v0.3.2
+++++++

Released on `Tue Feb 7 18:07:57 UTC 2012`.

- Command-line options support in :func:`pycom.main`
- :func:`pycom.nameserver` is thread-safe now
- Separated protocol-related server code into `pycom.server` module

v0.3.1
+++++++

Released on `Sun Feb 5 15:48:18 UTC 2012`.

- :class:`pycom.RemoteComponent` added to public API
- Refactored internals, simplified some private functions
- Bug fixes

v0.3.0
+++++++

Released on `Thu Feb 2 15:56:29 UTC 2012`.

- Renamed concept `invoker` to `component` (as in C++ API).
- Nameserver's `locate` method now takes `service` argument
- :func:`pycom.locate` now takes `service_name` argument
- Introduced :class:`pycom.BaseComponent`
- Sphinx docs are now built and installed on `setup.py install`
- Refactored internals
- Support for sessions - permanent storage across requests
- Major documentation update

v0.2.0
+++++++

Released on `Fri Jan 27 21:35:43 UTC 2012`.

- Nameserver's `locate` method now takes `as_list` argument
- Properly handle bugs in main routine
- Better logging
- Major documentation update

v0.1.1
+++++++

Released on `Thu Jan 19 21:17:15 UTC 2012`.

- Major documentation update
- More tests

v0.1.0
+++++++

Released on `Tue Jan 17 21:30:41 UTC 2012`.

- Initial release.
- Basic support for invoking remote methods.
- Simple nameserver implementation.
