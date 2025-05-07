libcarna
========

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

.. automodule:: libcarna
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance: