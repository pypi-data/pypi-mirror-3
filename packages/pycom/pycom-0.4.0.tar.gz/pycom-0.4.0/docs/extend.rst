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

.. autoclass:: pycom.zerojson.common.BaseCommand
   :members:

.. autofunction:: pycom.zerojson.common.dict_to_wire

.. autofunction:: pycom.zerojson.common.dict_from_wire

.. autoclass:: pycom.zerojson.call.CallCommand

   Some members signature differs from base class:

   .. automethod:: pycom.zerojson.call.CallCommand.request_to_dict

   .. automethod:: pycom.zerojson.call.CallCommand.response_to_dict

.. autofunction:: pycom.zerojson.client.detect_ns
