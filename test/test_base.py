import numpy as np

import carna
import testsuite


class SpatialMixin:

    ClientSpatialType = None
    client_spatial_init_kwargs = dict()

    def test__movable(self):
        node1 = self.ClientSpatialType(**self.client_spatial_init_kwargs)
        self.assertTrue(node1.is_movable)
        node1.is_movable = False
        self.assertFalse(node1.is_movable)

    def test__tag(self):
        node1 = self.ClientSpatialType(**self.client_spatial_init_kwargs)
        self.assertEqual(node1.tag, '')
        node1.tag = 'Test'
        self.assertEqual(node1.tag, 'Test')

    def test__localTransform(self):
        node1 = self.ClientSpatialType(**self.client_spatial_init_kwargs)
        np.testing.assert_array_almost_equal(node1.local_transform, np.eye(4))
        node1.local_transform = np.arange(16).reshape(4, 4)
        np.testing.assert_array_almost_equal(node1.local_transform, np.arange(16).reshape(4, 4))

    def test__worldTransform(self):
        node1 = carna.base.Node()
        node1.local_transform = np.eye(4) * 2
        node1.update_world_transform()
        node2 = self.ClientSpatialType(**self.client_spatial_init_kwargs)
        node1.attach_child(node2)
        node2.local_transform = np.eye(4) / 3
        node2.update_world_transform()
        np.testing.assert_array_almost_equal(node1.world_transform, np.eye(4) * 2)
        np.testing.assert_array_almost_equal(node2.world_transform, np.eye(4) * 2 / 3)

    def test__detach_from_parent(self):
        node1 = carna.base.Node()
        node2 = self.ClientSpatialType(**self.client_spatial_init_kwargs)
        self.assertFalse(node2.has_parent)
        node1.attach_child(node2)
        self.assertTrue(node2.has_parent)
        node2.detach_from_parent()
        self.assertFalse(node2.has_parent)


class Node(testsuite.CarnaTestCase, SpatialMixin):

    ClientSpatialType = carna.base.Node

    def test__tag(self):
        super().test__tag()
        node1 = carna.base.Node('Test 2')
        self.assertEqual(node1.tag, 'Test 2')

    def test__attach_child(self):
        node1 = carna.base.Node()
        self.assertEqual(node1.children(), 0)
        node2 = carna.base.Node()
        node1.attach_child(node2)
        self.assertEqual(node1.children(), 1)

    def test__attach_child__circular(self):
        node1 = carna.base.Node()
        node2 = carna.base.Node()
        node1.attach_child(node2)
        with self.assertRaises(RuntimeError):
            node2.attach_child(node1)

    def test__attach_child__nonfree(self):
        node1 = carna.base.Node()
        node2 = carna.base.Node()
        node3 = carna.base.Node()
        node1.attach_child(node2)
        with self.assertRaises(RuntimeError):
            node3.attach_child(node2)


class Camera(testsuite.CarnaTestCase, SpatialMixin):

    ClientSpatialType = carna.base.Camera

    def test__projection(self):
        camera = carna.base.Camera()
        camera.projection = np.arange(16).reshape(4, 4)
        np.testing.assert_array_almost_equal(camera.projection, np.arange(16).reshape(4, 4))

    def test__orthogonal_projection_hint(self):
        camera = carna.base.Camera()
        self.assertFalse(camera.orthogonal_projection_hint)
        camera.orthogonal_projection_hint = True
        self.assertTrue(camera.orthogonal_projection_hint)

    def test__view_transform(self):
        camera = carna.base.Camera()
        camera.update_world_transform()
        np.testing.assert_array_almost_equal(camera.view_transform, np.eye(4))
        camera.local_transform = 2 * np.eye(4)
        camera.update_world_transform()
        np.testing.assert_array_almost_equal(camera.view_transform, 0.5 * np.eye(4))


class Geometry(testsuite.CarnaTestCase, SpatialMixin):

    ClientSpatialType = carna.base.Geometry
    client_spatial_init_kwargs = dict(
        geometry_type=0,
    )

    def test__geometry_type(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        geoemtry2 = carna.base.Geometry(geometry_type=1)
        self.assertEqual(geoemtry1.geometry_type, 0)
        self.assertEqual(geoemtry2.geometry_type, 1)

    def test__features_count(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        self.assertEqual(geoemtry1.features_count, 0)


class Material(testsuite.CarnaTestCase):

    def setUp(self):
        super().setUp()
        self.material = carna.base.Material('solid')

    def test__color(self):
        self.material['color'] = (1, 0, 0)
        self.material['color'] = (1, 1, 0)

    def test__has_parameter(self):
        self.assertFalse(self.material.has_parameter('color'))
        self.material['color'] = (1, 0, 0)
        self.assertTrue(self.material.has_parameter('color'))

    def test__remove_parameter(self):
        self.material.remove_parameter('color')
        self.assertFalse(self.material.has_parameter('color'))
        self.material['color'] = (1, 0, 0)
        self.material.remove_parameter('color')
        self.assertFalse(self.material.has_parameter('color'))

# # ==========================
# # Math
# # ==========================

# assert np.allclose(base.math.scaling4f(1, 1, 1), np.eye(4))
# assert np.allclose(base.math.translation4f(0, 0, 0), np.eye(4))
# assert np.allclose(base.math.rotation4f([0, 1, 0], 0), np.eye(4))
