import gc

import libcarna.egl

import testsuite


class EGLContext(testsuite.LibCarnaTestCase):

    def test__init__(self):
        ctx = libcarna.egl.EGLContext()
        del ctx

    def test__stack(self):
        """
        Test destruction of the active EGL context while another EGL context still exists (and will be activated by LibCarna).
        """
        ctx1 = libcarna.egl.EGLContext()
        ctx2 = libcarna.egl.EGLContext()
        del ctx2
        gc.collect()
        del ctx1