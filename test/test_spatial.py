import libcarna

import testsuite

import numpy as np


class node(testsuite.LibCarnaTestCase):

    def setUp(self):
        super().setUp()
        self.root  = libcarna.node()
        self.node1 = libcarna.node(parent=self.root, local_transform=libcarna.translate(0, 0, 1))
        pivot = libcarna.node(parent=self.root)
        self.node2 = libcarna.node(parent=pivot, local_transform=libcarna.scale(0.5))
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
            volume.GEOMETRY_TYPE_VOLUME,
            self.array,
            parent=self.root,
            local_transform=libcarna.translate(0, 0, 5),
            spacing=(1, 1, 1),
        )
        self.root.update_world_transform()

    def test__transform_into_voxels_from(self):
        np.testing.assert_array_almost_equal(
            self.volume.transform_into_voxels_from(self.root).point(),
            np.array([32., 24., 5., 1.]),
        )
