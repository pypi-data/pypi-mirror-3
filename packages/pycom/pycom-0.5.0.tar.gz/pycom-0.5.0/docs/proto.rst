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

.. data:: extensions
    :noindex:

    (JSON object, optional) object with extensions data

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

.. data:: extensions
    :noindex:

    (JSON object, optional) object with extensions data

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

      .. data:: interfaces
         :noindex:

         (list of strings) interfaces to register

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

   .. method:: locate

      Locates service by interface and service name.
      Argument is a dictionary with the following keys:

      .. data:: interface
         :noindex:

         (string) interface to locate

      .. data:: service
         :noindex:

         (string, optional) service name to locate

      Result is a dictionary with the following keys:

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

      .. data:: interfaces
         :noindex:

         (list of strings) list of provided interfaces

   .. method:: list_services

      List all known services.
      Argument is a dictionary with the following keys:

      .. data:: interface
         :noindex:

         (string, optional) if present, return only services with interface that
         matches given regular expression from the beginning.
         See examples for *service*. Not that dots must be escaped in
         regular expressions!

      .. data:: service
         :noindex:

         (string, optional) if present, return only services with name that
         matches given regular expression from the beginning.
         E.g. ``/org/pycom/nameserver`` matches::

            /org/pycom
            .*/pycom
            /(org|com)/pycom
            /org/pycom/nameserver$

         but does NOT match::

            /pycom
            /org/pycom/nameserver/1

      Result is a list of dictionaries with the following keys:

      .. data:: address
         :noindex:

         (string) 0MQ address of service

      .. data:: service
         :noindex:

         (string) service name

      .. data:: interfaces
         :noindex:

         (list of strings) list of provided interfaces

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

    PREPARE ==> RUN ==> RESET

the easy one is (with the last stage being optional as well)::

    CALL ==> RESET

Request object itself is send either via ``PREPARE`` or via ``CALL``.
The difference between these to commands is that ``CALL`` cannot send
binary attachments to the service and returns it's result immediately.
On the contrary, ``PREPARE`` is able to handle attachments upload, but
returns only ``call_id`` field. Results are acquired via ``RUN``
command, after all attachments are uploaded. Attachments are sent by chunks,
using ``FPUT`` command (see below).

If you are receiving attachments, result of ``RUN`` or ``CALL`` contains
non-empty ``attachments`` field.
You receive attachments by chunks, using ``FGET`` command.
After all attachments are received (or if you do not want to receive them),
``RESET`` command is issued with ``call_id``.

``RESET`` command can be used at any moment by client side to indicate, that
it is not going to continue conversation. Any data temporary stored by server
will be discarded on receiving this command. If ``RUN`` does not return
attachments, ``RESET`` is called automatically (it's not an error to call
it once more, though).

The whole procedure looks like::

    PREPARE => FPUT => FPUT => ... => RUN => FGET => FGET => ... => RESET

while the shortest is just::

    CALL

Request fields
+++++++++++++++

Top-level request object always contains the following fields:

.. data:: version
    :noindex:

    (string) protocol version, should be ``1.0`` now

``CALL`` and ``PREPARE``
~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level request object also contains:

.. data:: interface
    :noindex:

    (string) requested interface name

.. data:: method
    :noindex:

    (string) requested method name

.. data:: session_id
    :noindex:

    (string, optional) current session identifier

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

.. data:: extensions
    :noindex:

    (JSON object, optional) object with extensions data

``RUN`` and ``RESET``
~~~~~~~~~~~~~~~~~~~~~~~

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

``PREPARE``
~~~~~~~~~~~~

.. data:: call_id
    :noindex:

    (string) current call identifier

``CALL`` and ``RUN``
~~~~~~~~~~~~~~~~~~~~~~

In addition to common fields, top-level response object also contains:

.. data:: call_id
    :noindex:

    (string) current call identifier

.. data:: session_id
    :noindex:

    (string, optional) current session identifier

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

.. data:: extensions
    :noindex:

    (JSON object, optional) object with extensions data

``FGET``, ``FPUT`` and ``RESET``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Response contains only common fields as stated above.
