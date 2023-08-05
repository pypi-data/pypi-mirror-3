Protocol Specification
=======================

PyCOM services talk to each other via `0MQ <http://www.zeromq.org/>`_
multipart messages via REP-REQ pair of sockets:

#. Command (only ``CALL`` is supported now, response will contain either ``OK``
   on success or ``FAIL`` on fatal protocol error)
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
