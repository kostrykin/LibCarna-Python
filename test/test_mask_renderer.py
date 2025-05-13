import libcarna
from . import testsuite


class mask_renderer(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        mask_renderer1 = libcarna.mask_renderer(
            GEOMETRY_TYPE_VOLUME,
            sr=500,
            color=libcarna.color.RED,
            fill=True,
        )
        mask_renderer2 = mask_renderer1.replicate()
        self.assertEqual(mask_renderer2.geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(mask_renderer2.sample_rate, 500)
        self.assertEqual(mask_renderer2.color, libcarna.color.RED)
        self.assertEqual(mask_renderer2.filling, True)
