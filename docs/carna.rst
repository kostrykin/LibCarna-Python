carna
=====

The objects in this module provide a simplified and more Pythonic convenience interface for the natively structured
wrappers in the respective sub-modules.

Example
-------

These can be used to, for example, quickly assemble a scene of multiple objects, and then render it into a NumPy array:

.. literalinclude:: ../test/test_integration.py
   :start-after: # .. OpaqueRenderingStage: example-setup-start
   :end-before: # .. OpaqueRenderingStage: example-setup-end
   :dedent: 8

Note on ``GEOMETRY_TYPE_OPAQUE``: A *geometry type* is an arbitrary integer constant, that establishes a relation
between the geometry nodes of a scene graph, and the corresponding rendering stages (see below for details).

It is very easy to just render the scene into a NumPy array:

.. literalinclude:: ../test/test_integration.py
   :start-after: # .. OpaqueRenderingStage: example-single-frame-start
   :end-before: # .. OpaqueRenderingStage: example-single-frame-end
   :dedent: 8

This is the image ``array`` rendered in the example:

.. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test.png
   :width: 400

However, it is much easier to visually grasp the information in a 3D scene by looking at it from different angles. For
this reason, there is a set of convenience functions that fascilitates creating animations, by rendering multiple
frames at once:

.. literalinclude:: ../test/test_integration.py
   :start-after: # .. OpaqueRenderingStage: example-animation-start
   :end-before: # .. OpaqueRenderingStage: example-animation-end
   :dedent: 8

In this example, the camera is rotated around the *center of the scene* (more precisely: around it's parent node, that
happens to be the ``root`` node of the scene). The scene is rendered from 50 different angles. For each angle, the
result is a NumPy array, that is stored in the list of ``frames``. This is our example animation:

.. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test__animated.png
   :width: 400

Geometry Types
--------------

Each scene might contain multiple types of renderable objects. At least one could distinguish between polygonal and
volumetric objects. Planes are certainly a third type: They are neither polygonal because they are infinitely extended,
nor are they volumetric. It is up to the user to choose a more fine-grained taxonomy if required. Note that each
rendering stage expects to be told which *geometry type* it should render. For example, by using two CuttingPlanesStage
instances with different values for their *geometry type*, one could render multiple cutting planes with different
windowing settings.

API
---

.. automodule:: carna
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance: