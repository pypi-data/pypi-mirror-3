Extending PyCOM
================

This section documents bits required to extend PyCOM.

Semi-public API
----------------

Interface Declaration
++++++++++++++++++++++

.. autoclass:: pycom.interfaces.Interface
   :members:

.. autoclass:: pycom.interfaces.Method
   :members:

High-level Remote Access API
+++++++++++++++++++++++++++++

.. autoclass:: pycom.protocol.RemoteComponent

Protocol Implementation
++++++++++++++++++++++++

.. autofunction:: pycom.protocol.request_to_wire

.. autofunction:: pycom.protocol.request_from_wire

.. autofunction:: pycom.protocol.response_to_wire

.. autofunction:: pycom.protocol.response_from_wire

.. autofunction:: pycom.protocol.send_request
