import libcarna

import testsuite


class drr(testsuite.LibCarnaTestCase):

    def test__replicate(self):
        GEOMETRY_TYPE_VOLUME = 1
        drr1 = libcarna.drr(
            GEOMETRY_TYPE_VOLUME,
            sr=400,
            waterat=1e-3,
            baseint=2,
            lothres=-200,
            upthres=+800,
            upmulti=2,
            inverse=True,
        )
        drr2 = drr1.replicate()
        self.assertEqual(drr2.geometry_type, GEOMETRY_TYPE_VOLUME)
        self.assertEqual(drr2.sample_rate, 400)
        self.assertAlmostEqual(drr2.water_attenuation, 1e-3)
        self.assertAlmostEqual(drr2.base_intensity, 2)
        self.assertEqual(drr2.lower_threshold, -200)
        self.assertEqual(drr2.upper_threshold, +800)
        self.assertAlmostEqual(drr2.upper_multiplier, 2)
        self.assertEqual(drr2.render_inverse, True)
