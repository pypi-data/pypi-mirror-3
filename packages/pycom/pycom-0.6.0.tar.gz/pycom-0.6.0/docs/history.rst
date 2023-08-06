Release History
================

v0.6.0
-------

Released on `Sat Apr 28 20:18:04 UTC 2012`.

Features:

- :class:`zerojson.Server` is more extensible now.
- Services are no longer stateful by default.
- Added ``stateful`` argument to :func:`pycom.interface`.
- :class:`pycom.ProxyContext` can be used to wrap a real :class:`pycom.Context`
- Optional authentication is working via :meth:`pycom.Context.authenticate`.
- ``context()`` method is added to :class:`zerojson.Request` on fly
- Added also :meth:`pycom.Context.user_info`
- :func:`pycom.method` and :class:`pycom.interfaces.Method` got ``attachments``
  argument (with introspection).
- Experimental binary attachments support.
- :class:`pycom.ProxyComponent` now generates methods with proper names
  and docstrings.
- Added ``authentication`` argument to :func:`pycom.interface` and support
  for configuring authentication policy.

v0.5.1
-------

Released on `Thu Apr 12 09:27:54 UTC 2012`.

In this version we dismiss the draft of the future protocol that existed for
some time. Binary attachments will be in-memory only and there will be
a service with remote FS semantics.

Features:

- Dropped ``PREPARE`` and ``RUN`` subcommands; never were part of public API.
- :meth:`pycom.Service.introspect` now returns content of ``introspection_data``
  attribute.

Bug fixes:

- :class:`zerojson.Future` objects now work properly when result is returned
  before ioloop is set and prevent result from being set twice.
- Argument ``message`` of :meth:`zerojson.Future.error` is no longer mandatory.
- :class:`pycom.Context` (and similar) objects should be thread-safe now.
- Dropped our async server implementation of :class:`pycom.Server`
  in favor of ``ZMQStream``.
- From now on we use copying operations when possible to reduce memory usage.

Old releases
-------------

v0.5.0
+++++++

Released on `Thu Mar 29 14:12:59 UTC 2012`.

In this release we separated ZeroJSON-related code into `zerojson` package.
Exceptions, utilities and some constants moved there too.
Other changes include:

- Refactored internals to decouple ZeroJSON from PyCOM
- :class:`pycom.RemoteComponent` is no longer part of public API -
  use :meth:`pycom.Context.connect` or :meth:`pycom.ProxyContext.connect`
- Dropped deprecated :func:`pycom.nameserver` and :func:`pycom.locate`
- Replaced :exc:`pycom.Error` by :exc:`pycom.RemoteError`
  (which is in fact :exc:`zerojson.RemoteError`)
- Client receives :exc:`pycom.SessionExpired` when session has expired
- Added :meth:`zerojson.Request.error`
- Added :class:`zerojson.Future`
- Simplified :func:`pycom.method` usage
- Added hooks for :class:`pycom.Context`

v0.4.2
+++++++

Released on `Sun Mar 11 17:23:39 UTC 2012`.

- Added :func:`pycom.ext.checks.check_argument`
- Fixed protocol and implementation of NameServer to reflect current demands:

  - Use :func:`pycom.ext.checks.check_argument` to validate input
  - Clarify service rewriting (fixes
    `Issue 4 <https://bitbucket.org/divius/pycom/issue/4>`_)
  - Drop outdated services (fixes
    `Issue 1 <https://bitbucket.org/divius/pycom/issue/1>`_)
  - When several results are available for `locate`, random one is chosen
  - `list_services` now accepts regular expressions (and `service` argument)
  - Rewritten test suite

- Better error messages on validation failures
- Refactored internals of `pycom.zerojson`
- Renamed :meth:`pycom.Service.__introspect__` =>
  :meth:`pycom.Service.introspect`
- :class:`pycom.Context` now takes *nameserver* argument for constructor
- Introduced :class:`pycom.ProxyContext` and :class:`pycom.ProxyComponent`
- Deprecated :func:`pycom.nameserver` and :func:`pycom.locate`
- Added :meth:`pycom.Context.connect`
- PyCOM is officially compatible with Python 3.1 now,
  thus all supported Python releases are covered

v0.4.1
+++++++

Released on `Fri Mar 2 16:49:46 UTC 2012`.

- :class:`pycom.Request` no longer has ``__slots__``
- Prehooks now take :class:`pycom.Request` as a parameter
- Introduced :class:`pycom.Response` object
- Posthooks now take :class:`pycom.Response` as a parameter
- Introduced :class:`pycom.Context` object
- Added :meth:`pycom.interfaces.Method.post_configure`
- Added *method_factory* argument to :func:`pycom.method`
- Added method's introspection support to :func:`pycom.method`;
  added ``results`` argument
- Added :class:`pycom.Service` base class with ``__introspect__`` remote method
- Added :meth:`pycom.BaseComponent.introspect`

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
