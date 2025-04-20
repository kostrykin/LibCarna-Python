import numpy as np

import carna
import carna.egl
import carna.presets
import testsuite

carna.base.configure_carna_log(True)


class FrameRenderer(testsuite.CarnaTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = carna.egl.EGLContext()
        self.frame_renderer = carna.base.FrameRenderer(self.ctx, list(), 800, 600)

    def tearDown(self):
        del self.ctx
        del self.frame_renderer
        super().tearDown()

    def test__gl_context(self):
        self.assertIs(self.frame_renderer.gl_context, self.ctx)

    def test__width(self):
        self.assertEqual(self.frame_renderer.width, 800)

    def test__height(self):
        self.assertEqual(self.frame_renderer.height, 600)

    def test__reshape(self):
        for tidx, fit_square in enumerate((True, False, None)):
            with self.subTest(fit_square=fit_square):
                if fit_square is None:
                    kwargs = dict()
                else:
                    kwargs = dict(fit_square=fit_square)
                self.frame_renderer.reshape(801 + tidx, 601 + tidx, **kwargs)
                self.assertEqual(self.frame_renderer.width, 801 + tidx)
                self.assertEqual(self.frame_renderer.height, 601 + tidx)

    def test__render(self):
        root = carna.base.Node()
        camera = carna.base.Camera()
        root.attach_child(camera)
        self.frame_renderer.render(camera)

    def test__render__with_root(self):
        root = carna.base.Node()
        camera = carna.base.Camera()
        root.attach_child(camera)
        self.frame_renderer.render(camera, root)


class OpaqueRenderingStage(testsuite.CarnaTestCase):

    GEOMETRY_TYPE_OPAQUE = 1

    def setUp(self):
        super().setUp()
        self.ctx = carna.egl.EGLContext()

    def tearDown(self):
        del self.ctx
        super().tearDown()

    # def test(self):
    #     surface = carna.base.Surface(self.ctx, 800, 600)

    #     # Create and configure frame renderer
    #     opaque_rendering_stage = carna.presets.OpaqueRenderingStage(self.GEOMETRY_TYPE_OPAQUE)
    #     frame_renderer = carna.base.FrameRenderer(self.ctx, [opaque_rendering_stage], surface.width, surface.height)

    #     # Create mesh
    #     box = carna.base.MeshFactory.create_box(40, 40, 40)

    #     # Create and configure materials
    #     red = carna.base.Material('unshaded')
    #     green = carna.base.Material('unshaded')
    #     red['color'] = (1, 0, 0)
    #     green['color'] = (0, 1, 0)

    #     # Create and configure scene
    #     box1 = carna.base.Geometry(self.GEOMETRY_TYPE_OPAQUE)
    #     box2 = carna.base.Geometry(self.GEOMETRY_TYPE_OPAQUE)
    #     box1.put_feature(opaque_rendering_stage.ROLE_DEFAULT_MESH, box)
    #     box2.put_feature(opaque_rendering_stage.ROLE_DEFAULT_MESH, box)
    #     box1.put_feature(opaque_rendering_stage.ROLE_DEFAULT_MATERIAL, red)
    #     box2.put_feature(opaque_rendering_stage.ROLE_DEFAULT_MATERIAL, green)
    #     root = carna.base.Node()
    #     root.attach_child(box1)
    #     root.attach_child(box2)
    #     box1.local_transform = carna.base.math.translation(-10, -10, -40)
    #     box2.local_transform = carna.base.math.translation(+10, +10, +40)
    #     camera = carna.base.Camera()
    #     root.attach_child(camera)
    #     camera.projection = carna.base.math.frustum(np.pi / 2, 1, 10, 200)
    #     camera.local_transform = carna.base.math.translation(0, 0, 350)

    #     # Render scene
    #     surface.begin()
    #     frame_renderer.render(camera)
    #     result = surface.end()

    def test(self):
        surface = carna.base.Surface(self.ctx, 800, 600)

        # Create and configure frame renderer
        opaque = carna.presets.OpaqueRenderingStage(self.GEOMETRY_TYPE_OPAQUE)
        renderer = carna.base.FrameRenderer(self.ctx, [opaque], surface.width, surface.height)

        # Create mesh
        box_mesh  = carna.base.MeshFactory.create_box(40, 40, 40)

        # Create and configure materials
        material1 = carna.base.Material('unshaded')
        material2 = carna.base.Material('unshaded')
        material1['color'] = [1, 0, 0, 1]
        material2['color'] = [0, 1, 0, 1]

        # Create and configure scene
        box1 = carna.base.Geometry(self.GEOMETRY_TYPE_OPAQUE)
        box2 = carna.base.Geometry(self.GEOMETRY_TYPE_OPAQUE)
        box1.put_feature(opaque.ROLE_DEFAULT_MESH, box_mesh)
        box1.put_feature(opaque.ROLE_DEFAULT_MATERIAL, material1)
        box2.put_feature(opaque.ROLE_DEFAULT_MESH, box_mesh)
        box2.put_feature(opaque.ROLE_DEFAULT_MATERIAL, material2)
        root = carna.base.Node()
        root.attach_child(box1)
        root.attach_child(box2)
        box1.local_transform = carna.base.math.translation(-10, -10, -40)
        box2.local_transform = carna.base.math.translation(+10, +10, +40)
        camera = carna.base.Camera()
        root.attach_child(camera)
        camera.projection = carna.base.math.frustum(np.pi / 2, 1, 10, 200)
        camera.local_transform = carna.base.math.translation(0, 0, 250)

        # Render scene
        surface.begin()
        renderer.render(camera)
        result = surface.end()