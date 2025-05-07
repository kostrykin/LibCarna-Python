import libcarna
import testsuite


class dvr(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        dvr1 = libcarna.dvr(
            GEOMETRY_TYPE_VOLUME,
            cmap='viridis',
            sr=400,
            transl=1,
            diffuse=0.5,
        )
        dvr2 = dvr1.replicate()
        self.assertEqual(dvr2.geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(dvr2.cmap.color_map.color_list, dvr1.cmap.color_map.color_list)
        self.assertEqual(dvr2.sample_rate, 400)
        self.assertEqual(dvr2.translucency, 1)
        self.assertEqual(dvr2.diffuse_light, 0.5)
