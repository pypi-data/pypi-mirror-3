Release History
================

0.3 series
-----------

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

0.2 series
-----------

v0.2.0
+++++++

Released on `Fri Jan 27 21:35:43 UTC 2012`.

- Nameserver's `locate` method now takes `as_list` argument
- Properly handle bugs in main routine
- Better logging
- Major documentation update

0.1 series
-----------

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
