carna
=====

The objects in this module provide a simplified convenience interface for the more complex wrappers in the respective
sub-modules.

Example
-------

These can be used to, for example, quickly assemble a scene of multiple objects, and then render it into a NumPy array:

.. literalinclude:: ../test/test_integration.py
   :start-after: # .. example-start
   :end-before: # .. example-end
   :dedent: 8

The rendered ``array`` is this image:

.. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test.png
   :width: 400
   :alt: Alternative text

API
---

.. automodule:: carna
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance: