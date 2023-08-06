Extending PyCOM
================

This section documents API bits required to extend PyCOM.

Semi-public API
----------------

.. autofunction:: pycom.logger

.. autofunction:: pycom.ioloop

.. autofunction:: pycom.create_task

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

Constants
++++++++++

.. describe:: pycom.constants

    Module with common constants for PyCOM:

    .. literalinclude:: ../pycom/constants.py
        :start-after: ###BEGIN
        :end-before: ###END
