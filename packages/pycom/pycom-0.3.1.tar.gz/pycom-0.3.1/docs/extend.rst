Extending PyCOM
================

This section documents API bits required to extend PyCOM.

Semi-public API
----------------

Interface Declaration
++++++++++++++++++++++

.. autoclass:: pycom.interfaces.Interface
   :members:

.. autoclass:: pycom.interfaces.Method
   :members:

Protocol Implementation
++++++++++++++++++++++++

.. autofunction:: pycom.protocol.request_to_wire

.. autofunction:: pycom.protocol.request_from_wire

.. autofunction:: pycom.protocol.response_to_wire

.. autofunction:: pycom.protocol.response_from_wire

.. autofunction:: pycom.protocol.detect_ns
