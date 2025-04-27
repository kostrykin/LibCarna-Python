import numpy as np

import carna.base
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

    def test__put_feature(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        feature1 = carna.base.Material('solid')
        feature2 = carna.base.Material('solid')
        geoemtry1.put_feature(10, feature1)
        self.assertEqual(geoemtry1.features_count, 1)
        geoemtry1.put_feature(11, feature1)
        self.assertEqual(geoemtry1.features_count, 1)
        geoemtry1.put_feature(10, feature2)
        self.assertEqual(geoemtry1.features_count, 2)

    def test__remove_feature__by_role(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        feature1 = carna.base.Material('solid')
        geoemtry1.put_feature(10, feature1)
        geoemtry1.remove_feature(10)
        self.assertEqual(geoemtry1.features_count, 0)

    def test__remove_feature__by_feature(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        feature1 = carna.base.Material('solid')
        geoemtry1.put_feature(10, feature1)
        geoemtry1.remove_feature(feature1)
        self.assertEqual(geoemtry1.features_count, 0)

    def test__clear_features(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        feature1 = carna.base.Material('solid')
        feature2 = carna.base.Material('solid')
        geoemtry1.put_feature(10, feature1)
        geoemtry1.put_feature(11, feature2)
        geoemtry1.clear_features()
        self.assertEqual(geoemtry1.features_count, 0)

    def test__has_feature(self):
        geoemtry1 = carna.base.Geometry(geometry_type=0)
        feature1 = carna.base.Material('solid')
        feature2 = carna.base.Material('solid')
        self.assertFalse(geoemtry1.has_feature(10))
        self.assertFalse(geoemtry1.has_feature(11))
        self.assertFalse(geoemtry1.has_feature(feature1))
        self.assertFalse(geoemtry1.has_feature(feature2))
        geoemtry1.put_feature(10, feature1)
        self.assertTrue (geoemtry1.has_feature(10))
        self.assertFalse(geoemtry1.has_feature(11))
        self.assertTrue (geoemtry1.has_feature(feature1))
        self.assertFalse(geoemtry1.has_feature(feature2))


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


class MeshFactory(testsuite.CarnaTestCase):

    def test__create_box(self):
        box = carna.base.MeshFactory.create_box( width=1, height=2, depth=3 )
        del box

    def test__create_ball(self):
        ball = carna.base.MeshFactory.create_ball( radius=1, degree=3 )
        del ball

    def test__create_point(self):
        point = carna.base.MeshFactory.create_point()
        del point


class MeshRenderingStage(testsuite.CarnaTestCase):

    def test(self):
        self.assertNotEqual(
            carna.base.MeshRenderingStage.ROLE_DEFAULT_MESH,
            carna.base.MeshRenderingStage.ROLE_DEFAULT_MATERIAL,
        )


class math(testsuite.CarnaTestCase):

    def test__ortho(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.ortho(left=-1, right=1, bottom=-1, top=1, z_near=0.1, z_far=1000),
            np.array(
                [
                    [1, 0,  0, 0],
                    [0, 1,  0, 0],
                    [0, 0, -0.002, -1.0002],
                    [0, 0,  0, 1],
                ],
            ),
        )

    def test__frustum(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.frustum(left=-1, right=1, bottom=-1, top=1, z_near=0.1, z_far=1000),
            np.array(
                [
                    [0.1, 0  ,  0, 0],
                    [0  , 0.1,  0, 0],
                    [0  , 0  , -1.0002, -0.20002],
                    [0  , 0  , -1, 0],
                ],
            ),
        )

    def test__frustum__by_fov(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.frustum(fov=np.pi / 2, height_over_width=1, z_near=0.1, z_far=1000),
            np.array(
                [
                    [1, 0,  0, 0],
                    [0, 1,  0, 0],
                    [0, 0, -1.0002, -0.20002],
                    [0, 0, -1, 0],
                ],
            ),
        )

    def test__deg2rad(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.deg2rad(180),
            np.pi,
        )

    def test__rad2deg(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.rad2deg(np.pi),
            180,
            decimal=4,
        )

    def test__rotation__axis_is_column_vector(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.rotation(axis=np.array([[0], [1], [0]]), radians=np.pi),
            np.array(
                [
                    [-1, 0,  0, 0],
                    [ 0, 1,  0, 0],
                    [ 0, 0, -1, 0],
                    [ 0, 0,  0, 1],
                ],
            ),
        )

    def test__rotation__axis_is_list(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.rotation(axis=[0, 1, 0], radians=np.pi),
            np.array(
                [
                    [-1, 0,  0, 0],
                    [ 0, 1,  0, 0],
                    [ 0, 0, -1, 0],
                    [ 0, 0,  0, 1],
                ],
            ),
        )

    def test__translation__offset_is_column_vector(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.translation(offset=np.array([[1], [2], [3]])),
            np.array(
                [
                    [1, 0, 0, 1],
                    [0, 1, 0, 2],
                    [0, 0, 1, 3],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__translation__offset_is_list(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.translation(offset=[1, 2, 3]),
            np.array(
                [
                    [1, 0, 0, 1],
                    [0, 1, 0, 2],
                    [0, 0, 1, 3],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__translation__offset_is_explicit(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.translation(tx=1, ty=2, tz=3),
            np.array(
                [
                    [1, 0, 0, 1],
                    [0, 1, 0, 2],
                    [0, 0, 1, 3],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__scaling__offset_is_column_vector(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.scaling(factors=np.array([[1], [2], [3]])),
            np.array(
                [
                    [1, 0, 0, 0],
                    [0, 2, 0, 0],
                    [0, 0, 3, 0],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__scaling__offset_is_list(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.scaling(factors=[1, 2, 3]),
            np.array(
                [
                    [1, 0, 0, 0],
                    [0, 2, 0, 0],
                    [0, 0, 3, 0],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__scaling__uniform_factor(self):
        f = 2.5
        np.testing.assert_array_almost_equal(
            carna.base.math.scaling(uniform_factor=f),
            np.array(
                [
                    [f, 0, 0, 0],
                    [0, f, 0, 0],
                    [0, 0, f, 0],
                    [0, 0, 0, 1],
                ],
            ),
        )

    def test__plane__by_distance(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.plane(normal=[0, 2, 0], distance=2),
            np.array(
                [
                    [0, -1, 0, 0],
                    [0,  0, 1, 2],
                    [1,  0, 0, 0],
                    [0,  0, 0, 1],
                ],
            ),
        )

    def test__plane__by_support(self):
        np.testing.assert_array_almost_equal(
            carna.base.math.plane(normal=[0, 2, 0], support=[0, 2, 0]),
            np.array(
                [
                    [0, -1, 0, 0],
                    [0,  0, 1, 2],
                    [1,  0, 0, 0],
                    [0,  0, 0, 1],
                ],
            ),
        )

    def test__plane__zero_normal(self):
        with self.assertRaises(RuntimeError):
            carna.base.math.plane(normal=[0, 0, 0], distance=0)


class Color(testsuite.CarnaTestCase):

    def test__eq__(self):
        self.assertTrue(carna.base.Color.WHITE == carna.base.Color.WHITE)
        self.assertTrue(carna.base.Color.WHITE != carna.base.Color.WHITE_NO_ALPHA)

    def test__init__4ub(self):
        self.assertEqual(carna.base.Color(255, 255, 255, 0), carna.base.Color.WHITE_NO_ALPHA)

    def test__init__array(self):
        self.assertEqual(carna.base.Color((1., 1., 1., 0.)), carna.base.Color.WHITE_NO_ALPHA)

    def test__rgba(self):
        self.assertEqual(carna.base.Color.GREEN.r, 0)
        self.assertEqual(carna.base.Color.GREEN.g, 255)
        self.assertEqual(carna.base.Color.GREEN.b, 0)
        self.assertEqual(carna.base.Color.GREEN.a, 255)

    def test__toarray(self):
        np.testing.assert_array_equal(carna.base.Color.GREEN.toarray(), (0., 1., 0., 1.))
