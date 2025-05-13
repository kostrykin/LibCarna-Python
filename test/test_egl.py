import gc

import libcarna.egl

import testsuite


class EGLContext(testsuite.LibCarnaTestCase):

    def test__init__(self):
        """
        Test simple creation and destruction of an EGL context.
        """
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

    def test__vendor(self):
        """
        Test the "vendor" string of the EGL context.
        """
        ctx = libcarna.egl.EGLContext()
        self.assertIsInstance(ctx.vendor, str)
        self.assertGreater(len(ctx.vendor), 0)
        print("*** EGL vendor: %s" % ctx.vendor)

    def test__renderer(self):
        """
        Test the "renderer" string of the EGL context.
        """
        ctx = libcarna.egl.EGLContext()
        self.assertIsInstance(ctx.renderer, str)
        self.assertGreater(len(ctx.renderer), 0)
        print("*** EGL renderer: %s" % ctx.renderer)
