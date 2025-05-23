import libcarna.helpers
import numpy as np

from . import testsuite


class VolumeGridHelper:

    def create(self):
        return self.VolumeGridHelper(
            native_resolution=(512, 512, 200),
        )
    
    def create_with_max_segment_bytesize(self):
        return self.VolumeGridHelper(
            native_resolution=(64, 64, 20),
            max_segment_bytesize=64 * 64 * 64 * 4,
        )

    def test__init(self):
        self.create()

    def test__init__with_max_segment_bytesize(self):
        self.create_with_max_segment_bytesize()
    
    def test__native_resolution(self):
        helper1 = self.create()
        helper2 = self.create_with_max_segment_bytesize()
        self.assertEqual(tuple(helper1.native_resolution), (512, 512, 200))
        self.assertEqual(tuple(helper2.native_resolution), (64, 64, 20))

    def test__load_intensities(self):
        np.random.seed(0)
        data = np.random.rand(64, 64, 20)
        helper = self.create_with_max_segment_bytesize()
        helper.load_intensities(data)

    def test__create_node__with_spacing(self):
        helper = self.create()
        helper.create_node(
            geometry_type=1,
            spacing=self.VolumeGridHelper.Spacing((0.1, 0.1, 0.2)),
        )

    def test__create_node__with_extent(self):
        helper = self.create()
        helper.create_node(
            geometry_type=1,
            extent=self.VolumeGridHelper.Extent((100, 100, 80)),
        )


class VolumeGridHelper_IntensityComponent:

    def test__intensity_role(self):
        helper = self.create()
        self.assertEqual(helper.intensities_role, self.VolumeGridHelper.DEFAULT_ROLE_INTENSITIES)
        for i in [helper.intensities_role + 1, helper.intensities_role + 2]:
            helper.intensities_role = i
            self.assertEqual(helper.intensities_role, i)

    def test__DEFAULT_ROLE_INTENSITIES(self):
        self.assertEqual(self.VolumeGridHelper.DEFAULT_ROLE_INTENSITIES, 0)


class VolumeGridHelper_NormalsComponent:

    def test__normals_role(self):
        helper = self.create()
        self.assertEqual(helper.normals_role, self.VolumeGridHelper.DEFAULT_ROLE_NORMALS)
        for i in [helper.normals_role + 1, helper.normals_role + 2]:
            helper.normals_role = i
            self.assertEqual(helper.normals_role, i)

    def test__DEFAULT_ROLE_NORMALS(self):
        self.assertEqual(self.VolumeGridHelper.DEFAULT_ROLE_NORMALS, 1)


class VolumeGridHelper_IntensityVolumeUInt16(
    testsuite.LibCarnaTestCase,
    VolumeGridHelper,
    VolumeGridHelper_IntensityComponent,
):

    VolumeGridHelper = libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt16


class VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8(
    testsuite.LibCarnaTestCase,
    VolumeGridHelper,
    VolumeGridHelper_IntensityComponent,
    VolumeGridHelper_NormalsComponent,
):

    VolumeGridHelper = libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8


class VolumeGridHelper_IntensityVolumeUInt8(
    testsuite.LibCarnaTestCase,
    VolumeGridHelper,
    VolumeGridHelper_IntensityComponent,
):

    VolumeGridHelper = libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt8


class VolumeGridHelper_IntensityVolumeUInt8_NormalMap3DInt8(
    testsuite.LibCarnaTestCase,
    VolumeGridHelper,
    VolumeGridHelper_IntensityComponent,
    VolumeGridHelper_NormalsComponent,
):

    VolumeGridHelper = libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt8_NormalMap3DInt8
