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

.. data:: result
    :noindex:

    (anything) any JSON entity that was returned from method

Nameserver remote API
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

      Locates service(s) by name.
      Argument is a dictionary with the following keys:

      .. data:: interface
         :noindex:

         (string) interface to locate

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
