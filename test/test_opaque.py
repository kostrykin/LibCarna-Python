import libcarna
import testsuite


class opaque(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_OPAQUE = 1
        opaque1 = libcarna.opaque(GEOMETRY_TYPE_OPAQUE)
        mipopaque2 = opaque1.replicate()
        self.assertEqual(mipopaque2.geometry_type, GEOMETRY_TYPE_OPAQUE)
