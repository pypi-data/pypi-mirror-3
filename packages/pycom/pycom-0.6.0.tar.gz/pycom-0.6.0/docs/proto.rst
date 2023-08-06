Protocol Specification
=======================

Low-level protocol
-------------------

PyCOM services talk to each other via `0MQ <http://www.zeromq.org/>`_
multipart messages via REP-REQ pair of sockets:

#. Command (only ``CALL`` is supported now, response will contain either ``OK``
   on success or ``FAIL`` on fatal protocol or server error)
#. `JSON <http://www.json.org/>`_ content in UTF-8.
#. (optional, not implemented yet) binary attachment

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

Standard services remote API
-----------------------------

NameServer
+++++++++++

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

Authenticator
++++++++++++++

.. class:: `org.pycom.authenticator`

   Remote interface for authenticating users. There is no such service in PyCOM
   distribution. Why? Well, because the exact authentication procedure may
   differ broadly. You have to write an appropriate service yourself.

   .. method:: authenticate

      Validate user's credentials and generate a random *token* for the
      current session.

      .. data:: user
         :noindex:

         (string) user name

      .. data:: credentials
         :noindex:

         (anything) any credentials the user can provide

      Result is a dictionary with the following keys:

      .. data:: token
         :noindex:

         (string) generated token for identifying user's session

   .. method:: validate

      Validate a token and return user's info.

      .. data:: token
         :noindex:

         (string) unique token

      Result is a dictionary with the following keys:

      .. data:: name
         :noindex:

         (string) user name

      .. data:: roles
         :noindex:

         (list of strings) user *roles*
         (exact interpretation depends on implementation)
