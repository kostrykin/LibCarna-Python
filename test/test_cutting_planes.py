import libcarna
import testsuite


class cutting_planes(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        GEOMETRY_TYPE_PLANE  = 2
        drr1 = libcarna.cutting_planes(
            GEOMETRY_TYPE_VOLUME,
            GEOMETRY_TYPE_PLANE,
            windowing_level=0.4,
            windowing_width=0.3,
        )
        drr2 = drr1.replicate()
        self.assertEqual(drr2.volume_geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(drr2.plane_geometry_type , GEOMETRY_TYPE_PLANE )
        self.assertAlmostEqual(drr2.windowing_level, 0.4)
        self.assertAlmostEqual(drr2.windowing_width, 0.3)
