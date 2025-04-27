import gc

import carna.egl

import testsuite


class EGLContext(testsuite.CarnaTestCase):

    def test__init__(self):
        ctx = carna.egl.EGLContext()
        del ctx

    def test__stack(self):
        """
        Test destruction of the active EGL context while another EGL context still exists (and will be activated by Carna).
        """
        ctx1 = carna.egl.EGLContext()
        ctx2 = carna.egl.EGLContext()
        del ctx2
        gc.collect()
        del ctx1