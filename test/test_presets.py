import libcarna.presets
import numpy as np

from . import testsuite


class VolumeRenderingStage(testsuite.LibCarnaTestCase):

    def create(self):
        return None  # VolumeRenderingStage has no public constructor

    def test__DEFAULT_SAMPLE_RATE(self):
        self.assertEqual(libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE, 200)

    def test__init__(self):
        self.create()

    def test__sample_rate(self):
        rs = self.create()
        if rs is not None:  # create is overridden in subclasses
            self.assertEqual(rs.sample_rate, libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE)
            for sample_rate in (rs.sample_rate + 100, rs.sample_rate + 200):
                rs.sample_rate = sample_rate
                self.assertEqual(rs.sample_rate, sample_rate)


class MaskRenderingStage(VolumeRenderingStage):

    def create(self):
        return libcarna.presets.MaskRenderingStage(geometry_type=1)

    def test__DEFAULT_ROLE_MASK(self):
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_ROLE_MASK, 2)

    def test__DEFAULT_COLOR(self):
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_COLOR.r, 0)
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_COLOR.g, 255)
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_COLOR.b, 0)
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_COLOR.a, 255)

    def test__DEFAULT_FILLING(self):
        self.assertEqual(libcarna.presets.MaskRenderingStage.DEFAULT_FILLING, True)

    def test__mask_role(self):
        rs = self.create()
        self.assertEqual(rs.mask_role, libcarna.presets.MaskRenderingStage.DEFAULT_ROLE_MASK)
        for mask_role in (rs.mask_role + 1, rs.mask_role + 2):
            rs = libcarna.presets.MaskRenderingStage(geometry_type=1, mask_role=mask_role)
            self.assertEqual(rs.mask_role, mask_role)

    def test__color(self):
        rs = self.create()
        self.assertEqual(rs.color, libcarna.presets.MaskRenderingStage.DEFAULT_COLOR)
        for color_r in (50, 100, 150):
            color = libcarna.base.Color(color_r, 255, 0, 255)
            rs.color = color
            self.assertEqual(rs.color, color)

    def test__filling(self):
        rs = self.create()
        self.assertEqual(rs.filling, True)
        for filling in (False, True):
            rs.filling = filling
            self.assertEqual(rs.filling, filling)


class ColorMapMixin:

    def test__color_map(self):
        """
        Test that, despite that `.color_map` returns a new `ColorMapView` each time it is called, the actual color map
        is shared between the `ColorMapView` instances.
        """
        rs = self.create()
        cmap1 = rs.color_map
        cmap1.write_linear_spline([libcarna.color.RED, libcarna.color.BLUE])
        cmap2 = rs.color_map
        self.assertEqual(cmap1.color_list, cmap2.color_list)

    def test__color_map__color_list(self):
        rs = self.create()
        self.assertEqual(rs.color_map.color_list[0], libcarna.color.BLACK_NO_ALPHA)
        self.assertEqual(rs.color_map.color_list[-1], libcarna.color.BLACK_NO_ALPHA)

    def test__color_map__write_linear_segment(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_segment(0.0, 0.5, libcarna.color.RED, libcarna.color.BLUE)
        self.assertEqual(cmap.color_list[0], libcarna.color.RED)
        self.assertEqual(cmap.color_list[len(cmap.color_list) // 2], libcarna.color.BLUE)

    def test__color_map__write_linear_spline(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_spline([libcarna.color.RED, libcarna.color.GREEN, libcarna.color.BLUE])
        self.assertEqual(cmap.color_list[0], libcarna.color.RED)
        self.assertEqual(cmap.color_list[len(cmap.color_list) // 2], libcarna.color.GREEN)
        self.assertEqual(cmap.color_list[-1], libcarna.color.BLUE)

    def test__color_map__clear(self):
        rs = self.create()
        cmap = rs.color_map
        cmap.write_linear_segment(0.0, 0.5, libcarna.color.RED, libcarna.color.BLUE)
        cmap.clear()
        self.assertEqual(cmap.color_list[0], libcarna.color.BLACK_NO_ALPHA)


class MIPStage(VolumeRenderingStage, ColorMapMixin):

    def create(self):
        return libcarna.presets.MIPStage(geometry_type=1)

    def test__ROLE_INTENSITIES(self):
        self.assertEqual(libcarna.presets.MIPStage.ROLE_INTENSITIES, 0)


class DVRStage(VolumeRenderingStage, ColorMapMixin):

    def create(self):
        return libcarna.presets.DVRStage(geometry_type=1)

    def test__ROLE_INTENSITIES(self):
        self.assertEqual(libcarna.presets.DVRStage.ROLE_INTENSITIES, 0)

    def test__ROLE_NORMALS(self):
        self.assertEqual(libcarna.presets.DVRStage.ROLE_NORMALS, 1)

    def test__DEFAULT_TRANSLUCENCY(self):
        self.assertEqual(libcarna.presets.DVRStage.DEFAULT_TRANSLUCENCY, 50)

    def test__DEFAULT_DIFFUSE_LIGHT(self):
        self.assertEqual(libcarna.presets.DVRStage.DEFAULT_DIFFUSE_LIGHT, 1)

    def test__translucency(self):
        rs = self.create()
        self.assertEqual(rs.translucency, libcarna.presets.DVRStage.DEFAULT_TRANSLUCENCY)
        for translucency in (0.3, 0.5, 0.7):
            rs.translucency = translucency
            self.assertAlmostEqual(rs.translucency, translucency, places=5)

    def test__diffuse_light(self):
        rs = self.create()
        self.assertEqual(rs.diffuse_light, libcarna.presets.DVRStage.DEFAULT_DIFFUSE_LIGHT)
        for diffuse_light in (0.3, 0.5, 0.7):
            rs.diffuse_light = diffuse_light
            self.assertAlmostEqual(rs.diffuse_light, diffuse_light, places=5)


class CuttingPlanesStage(testsuite.LibCarnaTestCase):

    def test__windowing_level(self):
        rs = libcarna.presets.CuttingPlanesStage(volume_geometry_type=1, plane_geometry_type=2)
        self.assertEqual(rs.windowing_level, libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_LEVEL)
        for windowing_level in (0.3, 0.5, 0.7):
            rs.windowing_level = windowing_level
            self.assertAlmostEqual(rs.windowing_level, windowing_level, places=5)

    def test__windowing_width(self):
        rs = libcarna.presets.CuttingPlanesStage(volume_geometry_type=1, plane_geometry_type=2)
        self.assertEqual(rs.windowing_width, libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_WIDTH)
        for windowing_width in (0.3, 0.5, 0.7):
            rs.windowing_level = windowing_width
            self.assertAlmostEqual(rs.windowing_level, windowing_width, places=5)

