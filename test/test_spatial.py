import numpy as np

import libcarna

from . import testsuite


class node(testsuite.LibCarnaTestCase):

    def setUp(self):
        super().setUp()
        self.root  = libcarna.node()
        self.node1 = libcarna.node(parent=self.root).translate_local(0, 0, 1)
        pivot = libcarna.node(parent=self.root)
        self.node2 = libcarna.node(parent=pivot).scale_local(0.5)
        self.root.update_world_transform()

    def test__transform_from__identity(self):
        np.testing.assert_array_almost_equal(self.node1.transform_from(self.node1).mat, np.eye(4))
        np.testing.assert_array_almost_equal(self. root.transform_from(self. root).mat, np.eye(4))

    def test__transform_from__node1_from_node2(self):
        np.testing.assert_array_almost_equal(
            self.node1.transform_from(self.node2).mat,
            np.linalg.inv(self.node1.world_transform) @ self.node2.world_transform,
        )

    def test__transform_from__node2_from_node1(self):
        np.testing.assert_array_almost_equal(
            self.node2.transform_from(self.node1).mat,
            np.linalg.inv(self.node2.world_transform) @ self.node1.world_transform,
        )


class volume(testsuite.LibCarnaTestCase):

    GEOMETRY_TYPE_VOLUME = 1

    def setUp(self):
        super().setUp()
        self.array = np.zeros((65, 49, 21), dtype=np.uint8)
        self.root = libcarna.node()
        self.volume = libcarna.volume(
            self.GEOMETRY_TYPE_VOLUME,
            self.array,
            parent=self.root,
            spacing=(1, 1, 1),
        ).translate_local(0, 0, 5)
        self.root.update_world_transform()

    def test__transform_into_voxels_from(self):
        np.testing.assert_array_almost_equal(
            self.volume.transform_into_voxels_from(self.root).point(),
            (32., 24., 5.,),
        )

    def test__extent(self):
        np.testing.assert_array_almost_equal(
            self.volume.extent,
            (64., 48., 20.),
        )

    def test__spacing(self):
        np.testing.assert_array_almost_equal(
            self.volume.spacing,
            (1., 1., 1.),
        )

    def test__int16__hu(self):
        """
        Test creating the volume from data in Hounsfield Units. All image identities are identical.
        """
        array = np.zeros((40, 30, 20), dtype=np.int16)
        assert list(np.unique(array)) == [0]  # precondition: all values are 0
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1), units='hu')
        np.testing.assert_array_almost_equal(
            volume.normalized([-1024, +3071]), [0, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 1]), [-1024, +3071],
        )

    def test__uint8__raw__full_range(self):
        """
        Test creating the volume from `uint8` data. The image intensities span the full range between 0 and 255.
        """
        array = np.zeros((40, 30, 20), dtype=np.uint8)
        array.fill(0)
        array.flat[0] = 0xFF
        assert list(np.unique(array)) == [0, 0xFF]  # precondition: values span the full range
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([0, 0x7F, 0xFF]), [0, 0x7F / 0xFF, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0x7F / 0xFF, 1]), [0, 0x7F, 0xFF],
        )

    def test__uint8__raw__part_range(self):
        """
        Test creating the volume from `uint8` data. The image intensities are between 100 and 150.
        """
        array = np.zeros((40, 30, 20), dtype=np.uint8)
        array.fill(100)
        array.flat[0] = 150
        assert list(np.unique(array)) == [100, 150]  # precondition: values are between 100 and 150
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([100, 125, 150]), [0, 0.5, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [100, 125, 150],
        )

    def test__uint8__raw__uniform(self):
        """
        Test creating the volume from `uint8` data. All image intensities are identical.
        """
        array = np.full((40, 30, 20), 3, dtype=np.uint8)
        assert list(np.unique(array)) == [3]  # precondition: all values are 3
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([1, 3, 5]), [0, 0, 0],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [3, 3, 3],
        )

    def test__uint16__raw__full_range(self):
        """
        Test creating the volume from `uint16` data. The image intensities span the full range between 0 and 0xFFFF.
        """
        array = np.zeros((40, 30, 20), dtype=np.uint16)
        array.fill(0)
        array.flat[0] = 0xFFFF
        assert list(np.unique(array)) == [0, 0xFFFF]  # precondition: values span the full range
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([0, 0x7FFF, 0xFFFF]), [0, 0x7FFF / 0xFFFF, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0x7FFF / 0xFFFF, 1]), [0, 0x7FFF, 0xFFFF],
        )

    def test__uint16__raw__part_range(self):
        """
        Test creating the volume from `uint16` data. The image intensities are between 100 and 150.
        """
        array = np.zeros((40, 30, 20), dtype=np.uint16)
        array.fill(100)
        array.flat[0] = 150
        assert list(np.unique(array)) == [100, 150]  # precondition: values are between 100 and 150
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([100, 125, 150]), [0, 0.5, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [100, 125, 150],
        )

    def test__uint16__raw__uniform(self):
        """
        Test creating the volume from `uint16` data. All image intensities are identical.
        """
        array = np.full((40, 30, 20), 3, dtype=np.uint16)
        assert list(np.unique(array)) == [3]  # precondition: all values are 3
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([1, 3, 5]), [0, 0, 0],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [3, 3, 3],
        )

    def test__float__raw(self):
        """
        Test creating the volume from `float` data. The image intensities are between -1 and +3.
        """
        array = np.zeros((40, 30, 20), dtype=float)
        array.fill(-1)
        array.flat[0] = +3
        assert list(np.unique(array)) == [-1, +3]  # precondition: values are between -1 and +3
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([-1, +1, +3]), [0, 0.5, 1],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [-1, +1, +3],
        )

    def test__float__raw__uniform(self):
        """
        Test creating the volume from `float` data. All image intensities are identical.
        """
        array = np.full((40, 30, 20), -3, dtype=float)
        assert list(np.unique(array)) == [-3]  # precondition: all values are -3
        volume = libcarna.volume(self.GEOMETRY_TYPE_VOLUME, array, spacing=(1, 1, 1))
        np.testing.assert_array_almost_equal(
            volume.normalized([-1, +1, +3]), [0, 0, 0],
        )
        np.testing.assert_array_almost_equal(
            volume.raw([0, 0.5, 1]), [-3, -3, -3],
        )
