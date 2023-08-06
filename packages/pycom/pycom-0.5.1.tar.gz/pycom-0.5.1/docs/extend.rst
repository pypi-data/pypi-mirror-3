Extending PyCOM
================

This section documents API bits required to extend PyCOM.

PyCOM Semi-public API
----------------------

.. autofunction:: pycom.logger

.. autofunction:: pycom.ioloop

.. autofunction:: pycom.create_task

Interface Declaration
++++++++++++++++++++++

.. autoclass:: pycom.interfaces.Interface
   :members:

.. autoclass:: pycom.interfaces.Method
   :members:

Other
++++++

.. autofunction:: pycom.nsclient.detect_ns

ZeroJSON Implementation
------------------------

Higher-level API
+++++++++++++++++

.. autoclass:: zerojson.Server
   :members:

.. autoclass:: zerojson.Client
   :members:

Commands Implementation
++++++++++++++++++++++++

.. autoclass:: zerojson.common.BaseCommand
   :members:

.. autofunction:: zerojson.common.dict_to_wire

.. autofunction:: zerojson.common.dict_from_wire

.. autoclass:: zerojson.call.CallCommand

Constants
----------

.. describe:: pycom.constants

    Module with common constants for PyCOM:

    .. literalinclude:: ../pycom/constants.py
        :start-after: ###BEGIN
        :end-before: ###END

.. describe:: zerojson.constants

    Module with common constants for ZeroJSON protocol:

    .. literalinclude:: ../zerojson/constants.py
        :start-after: ###BEGIN
        :end-before: ###END
