import carna.helpers
import numpy as np

import testsuite


class VolumeGridHelper_IntensityVolumeUInt16(testsuite.CarnaTestCase):

    def test__init(self):
        return carna.helpers.VolumeGridHelper_IntensityVolumeUInt16(native_resolution=(512, 512, 200))

    def test__init__with_max_segment_bytesize(self):
        return carna.helpers.VolumeGridHelper_IntensityVolumeUInt16(
            native_resolution=(64, 64, 20),
            max_segment_bytesize=64 * 64 * 64 * 4,
        )
    
    def test__native_resolution(self):
        helper1 = self.test__init()
        helper2 = self.test__init__with_max_segment_bytesize()
        self.assertEqual(tuple(helper1.native_resolution), (512, 512, 200))
        self.assertEqual(tuple(helper2.native_resolution), (64, 64, 20))

    def test__load_intensities(self):
        np.random.seed(0)
        data = np.random.rand(64, 64, 20)
        helper = self.test__init__with_max_segment_bytesize()
        helper.load_intensities(data)

    def test__intensity_role(self):
        helper = self.test__init()
        self.assertEqual(helper.intensities_role, 0)
        for i in [1, 2]:
            helper.intensities_role = i
            self.assertEqual(helper.intensities_role, i)