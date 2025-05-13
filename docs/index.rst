libcarna-python
===============

These are the Python bindings for the LibCarna library. The documentation of the original LibCarna library can be found at:
https://kostrykin.github.io/LibCarna/html.


Getting Started
---------------

The easiest way to install and use the library is to use our pre-built
`Conda <https://www.anaconda.com/docs/getting-started/miniconda>`_ packages::

   conda install bioconda::libcarna-python

To get started, it is best to consider our `Examples`_ below.

.. note::
   If you encounter an error similar to `"Failed expression: pimpl->eglDpy != EGL_NO_DISPLAY"`, then you must install
   an EGL implementation suitable for your rendering hardware. For example, on Ubuntu Linux, ``sudo apt install
   libegl1`` installs a meta package that automatically chooses the right implementation, or ``libegl-mesa0`` for
   software rendering.

Examples
--------

.. toctree::
   
   examples/introduction
   examples/cells
   examples/cthead

API
---

.. toctree::
   :maxdepth: 1

   libcarna
   libcarna.base
   libcarna.base.math
   libcarna.data
   libcarna.egl
   libcarna.helpers
   libcarna.presets