import carna.egl

import testsuite


class EGLContext(testsuite.CarnaTestCase):

    def test(self):
        ctx = carna.egl.EGLContext()
        del ctx