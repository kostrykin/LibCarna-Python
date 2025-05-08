import numpy as np

import libcarna
import testsuite


class cutting_planes(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        GEOMETRY_TYPE_PLANE  = 2
        cp1 = libcarna.cutting_planes(
            GEOMETRY_TYPE_VOLUME,
            GEOMETRY_TYPE_PLANE,
            cmap='viridis',
            clim=(0.3, 0.4),
        )
        cp2 = cp1.replicate()
        self.assertEqual(cp2.volume_geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(cp2.plane_geometry_type , GEOMETRY_TYPE_PLANE )
        self.assertEqual(cp2.cmap.colormap.color_list, cp1.cmap.colormap.color_list)
        np.testing.assert_array_almost_equal(cp2.cmap.limits(), (0.3, 0.4))
