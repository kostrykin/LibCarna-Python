import numpy as np
import scipy.ndimage as ndi

import carna
import testsuite


class VolumeGridHelper_IntensityVolumeUInt16(testsuite.CarnaTestCase):

    def test(self):
        np.random.seed(0)
        data = np.random.rand(64, 64, 20)
        helper = carna.helpers.VolumeGridHelper_IntensityVolumeUInt16(
            native_resolution=data.shape,
        )
        helper.load_intensities(data)
        node = helper.create_node(
            geometry_type=1,
            spacing=carna.helpers.VolumeGridHelper_IntensityVolumeUInt16.Spacing((0.1, 0.1, 0.2)),
        )
        root = carna.node()
        root.attach_child(node)


class FrameRenderer(testsuite.CarnaTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = carna.egl_context()
        self.frame_renderer = carna.frame_renderer(self.ctx, 800, 600)

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

    def test__render__without_stages(self):
        root = carna.node()
        camera = carna.camera(parent=root)
        self.frame_renderer.render(camera)

    def test__render__without_stages__with_root(self):
        root = carna.node()
        camera = carna.camera(parent=root)
        self.frame_renderer.render(camera, root)

    def test__append_stage(self):
        opaque = carna.opaque_renderer(0)
        self.frame_renderer.append_stage(opaque)

    def test__render(self):
        opaque = carna.opaque_renderer(0)
        self.frame_renderer.append_stage(opaque)
        root = carna.node()
        camera = carna.camera()
        root.attach_child(camera)
        self.frame_renderer.render(camera)


class OpaqueRenderingStage(testsuite.CarnaRenderingTestCase):

    def setUp(self):
        # .. OpaqueRenderingStage: example-setup-start
        GEOMETRY_TYPE_OPAQUE = 1

        # Create and configure frame renderer
        opaque = carna.opaque_renderer(GEOMETRY_TYPE_OPAQUE)
        r = carna.renderer(800, 600, [opaque])

        # Create mesh
        box_mesh = carna.mesh_factory.create_box(40, 40, 40)

        # Create and configure materials
        material1 = carna.material('unshaded', color=[1, 0, 0, 1])
        material2 = carna.material('unshaded', color=[0, 1, 0, 1])

        # Create and configure scene
        root = carna.node()
        carna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            local_transform=carna.math.translation(-10, -10, -40),
            features={
                opaque.ROLE_DEFAULT_MESH: box_mesh,
                opaque.ROLE_DEFAULT_MATERIAL: material1,
            },
        )
        carna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            local_transform=carna.math.translation(+10, +10, +40),
            features={
                opaque.ROLE_DEFAULT_MESH: box_mesh,
                opaque.ROLE_DEFAULT_MATERIAL: material2,
            },
        )
        camera = carna.camera(
            parent=root,
            projection=r.frustum(fov=np.pi / 2, z_near=1, z_far=1e3),
            local_transform=carna.math.translation(0, 0, 250),
        )
        # .. OpaqueRenderingStage: example-setup-end

        self.r, self.camera = r, camera

    def test(self):
        r, camera = self.r, self.camera

        # .. OpaqueRenderingStage: example-single-frame-start
        array = r.render(camera)
        # .. OpaqueRenderingStage: example-single-frame-end

        # Verify result
        self.assert_image_almost_expected(array)

    def test__animated(self):
        r, camera = self.r, self.camera

        # Render the scene once
        # .. OpaqueRenderingStage: example-animation-start
        # Define animation
        animation = carna.animation(
            [
                carna.animation.rotate_local(camera)
            ],
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))
        # .. OpaqueRenderingStage: example-animation-end

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class MaskRenderingStage(testsuite.CarnaRenderingTestCase):

    def setUp(self):
        # .. MaskRenderingStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2

        # Create and configure frame renderer
        mask_rendering = carna.mask_renderer(GEOMETRY_TYPE_VOLUME)
        mask_rendering.render_borders = True
        r = carna.renderer(800, 600, [mask_rendering])

        # Create volume
        np.random.seed(0)
        data = (
            ndi.gaussian_filter(np.random.rand(64, 64, 20), 10) > 0.5
        )

        # Create and configure scene
        root = carna.node()
        carna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )
        camera = carna.camera(
            parent=root,
            projection=r.frustum(fov=np.pi / 2, z_near=1, z_far=500),
            local_transform=carna.math.translation(0, 0, 100),
        )
        # .. MaskRenderingStage: example-setup-end

        self.r, self.camera = r, camera

    def test(self):
        r, camera = self.r, self.camera

        # Render scene
        array = r.render(camera)

        # Verify result
        self.assert_image_almost_expected(array)

    def test__animated(self):
        r, camera = self.r, self.camera

        # Define animation
        animation = carna.animation(
            [
                carna.animation.rotate_local(camera)
            ],
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))

        # Verify result
        self.assert_image_almost_expected(np.array(frames))