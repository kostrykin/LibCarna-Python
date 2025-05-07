import libcarna
import testsuite


class mip(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        mip1 = libcarna.mip(
            GEOMETRY_TYPE_VOLUME,
            cmap='jet',
            sr=400,
        )
        mip2 = mip1.replicate()
        self.assertEqual(mip2.geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(mip2.cmap.color_map.color_list, mip1.cmap.color_map.color_list)
        self.assertEqual(mip2.sample_rate, 400)
