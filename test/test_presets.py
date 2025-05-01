import carna.presets
import numpy as np

import testsuite


class VolumeRenderingStage(testsuite.CarnaTestCase):

    def create(self):
        return None  # VolumeRenderingStage has no public constructor

    def test__DEFAULT_SAMPLE_RATE(self):
        self.assertEqual(carna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE, 200)

    def test__init__(self):
        self.create()

    def test__sample_rate(self):
        rs = self.create()
        if rs is not None:  # create is overridden in subclasses
            self.assertEqual(rs.sample_rate, carna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE)
            for sample_rate in (rs.sample_rate + 100, rs.sample_rate + 200):
                rs.sample_rate = sample_rate
                self.assertEqual(rs.sample_rate, sample_rate)


class MaskRenderingStage(VolumeRenderingStage):

    def create(self):
        return carna.presets.MaskRenderingStage(geometry_type=1)

    def test__DEFAULT_ROLE_MASK(self):
        self.assertEqual(carna.presets.MaskRenderingStage.DEFAULT_ROLE_MASK, 2)

    def test__DEFAULT_COLOR(self):
        self.assertEqual(carna.presets.MaskRenderingStage.DEFAULT_COLOR.r, 0)
        self.assertEqual(carna.presets.MaskRenderingStage.DEFAULT_COLOR.g, 255)
        self.assertEqual(carna.presets.MaskRenderingStage.DEFAULT_COLOR.b, 0)
        self.assertEqual(carna.presets.MaskRenderingStage.DEFAULT_COLOR.a, 255)

    def test__mask_role(self):
        rs = self.create()
        self.assertEqual(rs.mask_role, carna.presets.MaskRenderingStage.DEFAULT_ROLE_MASK)
        for mask_role in (rs.mask_role + 1, rs.mask_role + 2):
            rs = carna.presets.MaskRenderingStage(geometry_type=1, mask_role=mask_role)
            self.assertEqual(rs.mask_role, mask_role)

    def test__color(self):
        rs = self.create()
        self.assertEqual(rs.color(), carna.presets.MaskRenderingStage.DEFAULT_COLOR)
        for color_r in (50, 100, 150):
            color = carna.base.Color(color_r, 255, 0, 255)
            rs.set_color(color)
            self.assertEqual(rs.color(), color)

    def test__render_borders(self):
        rs = self.create()
        self.assertEqual(rs.render_borders, False)
        for render_borders in (True, False):
            rs.render_borders = render_borders
            self.assertEqual(rs.render_borders, render_borders)


class MIPStage(VolumeRenderingStage):

    def create(self):
        return carna.presets.MIPStage(geometry_type=1)

    def test__ROLE_INTENSITIES(self):
        self.assertEqual(carna.presets.MIPStage.ROLE_INTENSITIES, 0)

    def test__color_map(self):
        """
        Test that, despite that `.color_map` returns a new `ColorMapView` each time it is called, the actual color map
        is shared between the `ColorMapView` instances.
        """
        rs = self.create()
        cmap1 = rs.color_map
        cmap1.write_linear_spline([carna.color.RED, carna.color.BLUE])
        cmap2 = rs.color_map
        self.assertEqual(cmap1.color_list, cmap2.color_list)

    def test__color_map__color_list(self):
        rs = self.create()
        self.assertEqual(rs.color_map.color_list[0], carna.color.BLACK_NO_ALPHA)
        self.assertEqual(rs.color_map.color_list[-1], carna.color.BLACK_NO_ALPHA)

    def test__color_map__write_linear_segment(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_segment(0.0, 0.5, carna.color.RED, carna.color.BLUE)
        self.assertEqual(cmap.color_list[0], carna.color.RED)
        self.assertEqual(cmap.color_list[len(cmap.color_list) // 2], carna.color.BLUE)

    def test__color_map__write_linear_spline(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_spline([carna.color.RED, carna.color.GREEN, carna.color.BLUE])
        self.assertEqual(cmap.color_list[0], carna.color.RED)
        self.assertEqual(cmap.color_list[len(cmap.color_list) // 2], carna.color.GREEN)
        self.assertEqual(cmap.color_list[-1], carna.color.BLUE)

    def test__color_map__clear(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_segment(0.0, 0.5, carna.color.RED, carna.color.BLUE)
        cmap.clear()
        self.assertEqual(cmap.color_list[0], carna.color.BLACK_NO_ALPHA)


class CuttingPlanesStage(testsuite.CarnaTestCase):

    def test__windowing_level(self):
        rs = carna.presets.CuttingPlanesStage(volume_geometry_type=1, plane_geometry_type=2)
        self.assertEqual(rs.windowing_level, carna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_LEVEL)
        for windowing_level in (0.3, 0.5, 0.7):
            rs.windowing_level = windowing_level
            self.assertAlmostEqual(rs.windowing_level, windowing_level, places=5)

    def test__windowing_width(self):
        rs = carna.presets.CuttingPlanesStage(volume_geometry_type=1, plane_geometry_type=2)
        self.assertEqual(rs.windowing_width, carna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_WIDTH)
        for windowing_width in (0.3, 0.5, 0.7):
            rs.windowing_level = windowing_width
            self.assertAlmostEqual(rs.windowing_level, windowing_width, places=5)

