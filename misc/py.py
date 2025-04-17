import atexit
import carna
import carna.base
import carna.egl
import numpy as np
import warnings


version    = carna.version
py_version = carna.py_version


# Create the OpenGL context when module is loaded
ctx = carna.egl.Context.create()

# Release the OpenGL context when module is unloaded
@atexit.register
def shutdown():
    ctx.free()
