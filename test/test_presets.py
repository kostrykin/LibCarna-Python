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

    def test__append_layer(self):
        layer = carna.presets.MIPLayer(0, 1, carna.base.Color.RED)
        rs = self.create()
        rs.append_layer(layer)

    def test__remove_layer(self):
        layer1 = carna.presets.MIPLayer(0, 1, carna.base.Color.RED)
        layer2 = carna.presets.MIPLayer(0, 1, carna.base.Color.GREEN)
        rs = self.create()
        rs.append_layer(layer1)
        rs.remove_layer(layer1)
        rs.append_layer(layer2)
