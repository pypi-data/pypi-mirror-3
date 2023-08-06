Protocol Specification
=======================

Low-level protocol
-------------------

PyCOM services talk to each other via `0MQ <http://www.zeromq.org/>`_

multipart messages via REP-REQ pair of sockets:

#. Command (only ``CALL`` is supported now, response will contain either ``OK``

   on success or ``FAIL`` on fatal protocol or server error)

#. `JSON <http://www.json.org/>`_ content in UTF-8.

Top-level request object contains the following properties:

.. data:: version
   :noindex:

   (string) protocol version, should be ``1.0`` now

.. data:: interface
   :noindex:

   (string) requested interface name (see below)

.. data:: method
    :noindex:

    (string) requested method name

.. data:: session_id
    :noindex:

    (string or null, optional) current session identifier

.. data:: args
    :noindex:

    (anything) any JSON entity to be passed as an argument to method

Top-level response object contains the following properties:

.. data:: code
    :noindex:

    (number) result code (0 for success)

.. data:: error
    :noindex:

    (string, optional) error message

.. data:: session_id
    :noindex:

    (string or null) current session identifier

.. data:: result
    :noindex:

    (anything) any JSON entity that was returned from method

NameServer remote API
----------------------

.. class:: `org.pycom.nameserver`

   Remote interface for registering and locating interfaces and services.

   .. method:: stat

      Ping method. Can be used to check whether nameserver is alive.
      Will return some statistics in the future.

   .. method:: register

      Registers interface.
      Argument is a dictionary with the following keys:

      .. data:: interface
         :noindex:

         (string) interface to register

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

   .. method:: locate

      Locates service(s) by interface and service name.
      Argument is a dictionary with the following keys:

      .. data:: interface
         :noindex:

         (string) interface to locate

      .. data:: service
         :noindex:

         (string, optional) service name to locate

      .. data:: as_list
         :noindex:

         (boolean, optional, default `False`) if set to True,
         method will return list of services instead of first one

      Result is a dictionary (or list of dictionaries - see `as_list` above)
      with the following keys:

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

   .. method:: list_services

      List all known services.

      Result is a list of dictionaries with the following keys:

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

Next protocol draft
--------------------

PyCOM services talk to each other via `0MQ <http://www.zeromq.org/>`_
multi-part messages via REP-REQ pair of sockets:

#. Command name (for response ``OK``,
   ``FAIL`` for unrecoverable protocol failure)
#. `JSON <http://www.json.org/>`_ content in UTF-8.
#. (only ``FPUT`` and ``FGET`` commands) binary attachment

There are several ways of invoking remote command. The most complicated of them
requires at least three request-reply pairs, the last being mostly optional::

    CALL ==> FINISH ==> RESET

The body of ``CALL`` contains the whole request object
with attachments listed in ``attachments`` section (see below),
response will contain ``call_id`` field, which you will send in the ``FINISH``
body after transfer is complete. Attachments are sent by chunks, using
``FPUT`` command (see below).

If you are receiving attachments, result of ``FINISH`` contains
non-empty ``attachments``.
You receive attachments by chunks, using ``FGET`` command.
After all attachments are received (or if you do not want to receive them),
``RESET`` command is issued with ``call_id``.

``RESET`` command can be used at any moment by client side to indicate, that
it is not going to continue conversation. Any data temporary stored by server
will be discarded on receiving this command. If ``FINISH`` does not return
attachments, ``RESET`` is called automatically.

The whole procedure looks like::

    CALL => FPUT => FPUT => ... => FINISH => FGET => FGET => ... => RESET

while the shortest is::

    CALL => FINISH

Request fields
+++++++++++++++

Top-level request object always contains the following fields:

.. data:: version
    :noindex:

    (string) protocol version, should be ``1.1`` now

Request for ``CALL``
~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level request object also contains:

.. data:: interface
    :noindex:

    (string) requested interface name

.. data:: method
    :noindex:

    (string) requested method name

.. data:: session_id
    :noindex:

    (string or null, optional) current session identifier

.. data:: args
    :noindex:

    (anything) any JSON entity to be passed as an argument to method

.. data:: attachments
    :noindex:

    (object) JSON object,
    with field names being attachments identifiers,
    values being objects with the following fields:

    .. data:: size
        :noindex:

        (integer) attachment size in bytes

``FINISH`` and ``RESET``
~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level request object also contains:

.. data:: call_id
    :noindex:

    (string) prepared call identifier

``FGET`` and ``FPUT``
~~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level request object also contains:

.. data:: call_id
    :noindex:

    (string) prepared call identifier

.. data:: attachment
    :noindex:

    (string) attachment identifier

.. data:: offset
    :noindex:

    (integer) offset to write/read at

Response fields
++++++++++++++++

Top-level response object always contains the following fields:

.. data:: code
    :noindex:

    (number) result code (0 for success)

.. data:: error
    :noindex:

    (string, optional) error message

Response to ``CALL``
~~~~~~~~~~~~~~~~~~~~~

.. data:: call_id
    :noindex:

    (string) current call identifier

Response to ``FINISH``
~~~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level response object also contains:

.. data:: call_id
    :noindex:

    (string) current call identifier

.. data:: session_id
    :noindex:

    (string or null) current session identifier

.. data:: result
    :noindex:

    (anything) any JSON entity that was returned from method

.. data:: attachments
    :noindex:

    (object) JSON object,
    with field names being attachments identifiers,
    values being objects with the following fields:

    .. data:: size
        :noindex:

        (integer) attachment size in bytes

``FGET``, ``FPUT`` and ``RESET``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Response contains only common fields as stated above.
