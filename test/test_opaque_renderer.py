import libcarna
import testsuite


class opaque_renderer(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_OPAQUE = 1
        opaque_renderer1 = libcarna.opaque_renderer(GEOMETRY_TYPE_OPAQUE)
        mipopaque_renderer2 = opaque_renderer1.replicate()
        self.assertEqual(mipopaque_renderer2.geometry_type, GEOMETRY_TYPE_OPAQUE)
