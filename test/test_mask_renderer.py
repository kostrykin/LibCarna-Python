import libcarna
import testsuite


class mask_renderer(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        MASK_ROLE = 2
        mask_renderer1 = libcarna.mask_renderer(
            GEOMETRY_TYPE_VOLUME,
            MASK_ROLE,
            color=libcarna.color.RED,
            fill=True,
        )
        mask_renderer2 = mask_renderer1.replicate()
        self.assertEqual(mask_renderer2.geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(mask_renderer2.mask_role, MASK_ROLE)
        self.assertEqual(mask_renderer2.color, libcarna.color.RED)
        self.assertEqual(mask_renderer2.filling, True)
