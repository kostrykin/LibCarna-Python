import numpy as np
import scipy.ndimage as ndi

import libcarna
import testsuite


class VolumeGridHelper_IntensityVolumeUInt16(testsuite.LibCarnaTestCase):

    def test(self):
        np.random.seed(0)
        data = np.random.rand(64, 64, 20)
        helper = libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt16(
            native_resolution=data.shape,
        )
        helper.load_intensities(data)
        node = helper.create_node(
            geometry_type=1,
            spacing=libcarna.helpers.VolumeGridHelper_IntensityVolumeUInt16.Spacing((0.1, 0.1, 0.2)),
        )
        root = libcarna.node()
        root.attach_child(node)


class FrameRenderer(testsuite.LibCarnaTestCase):

    def setUp(self):
        super().setUp()
        self.ctx = libcarna.egl_context()
        self.frame_renderer = libcarna.frame_renderer(self.ctx, 800, 600)

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
        root = libcarna.node()
        camera = libcarna.camera(parent=root)
        self.frame_renderer.render(camera)

    def test__render__without_stages__with_root(self):
        root = libcarna.node()
        camera = libcarna.camera(parent=root)
        self.frame_renderer.render(camera, root)

    def test__append_stage(self):
        opaque = libcarna.opaque(0)
        self.frame_renderer.append_stage(opaque)

    def test__render(self):
        opaque = libcarna.opaque(0)
        self.frame_renderer.append_stage(opaque)
        root = libcarna.node()
        camera = libcarna.camera()
        root.attach_child(camera)
        self.frame_renderer.render(camera)


class OpaqueRenderingStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. OpaqueRenderingStage: example-setup-start
        GEOMETRY_TYPE_OPAQUE = 1

        # Create and configure frame renderer
        opaque = libcarna.opaque(GEOMETRY_TYPE_OPAQUE)
        r = libcarna.renderer(800, 600, [opaque])

        # Create mesh
        box_mesh = libcarna.mesh_factory.create_box(40, 40, 40)

        # Create and configure materials
        material1 = libcarna.material('solid', color=[1, 0, 0, 1])
        material2 = libcarna.material('solid', color=[0, 1, 0, 1])

        # Create and configure scene
        root = libcarna.node()
        libcarna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            local_transform=libcarna.translate(-10, -10, -40),
            features={
                opaque.ROLE_DEFAULT_MESH: box_mesh,
                opaque.ROLE_DEFAULT_MATERIAL: material1,
            },
        )
        libcarna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            local_transform=libcarna.translate(+10, +10, +40),
            features={
                opaque.ROLE_DEFAULT_MESH: box_mesh,
                opaque.ROLE_DEFAULT_MATERIAL: material2,
            },
        )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=1e3),
            local_transform=libcarna.translate(0, 0, 250),
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

        # .. OpaqueRenderingStage: example-animation-start
        # Define animation
        animation = libcarna.animate(
            libcarna.animate.rotate_local(camera),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))
        # .. OpaqueRenderingStage: example-animation-end

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class MaskRenderingStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. MaskRenderingStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2

        # Create and configure frame renderer
        mask_rendering = libcarna.mask_renderer(GEOMETRY_TYPE_VOLUME)
        mask_rendering.render_borders = True
        r = libcarna.renderer(800, 600, [mask_rendering])

        # Create volume
        np.random.seed(0)
        data = (
            ndi.gaussian_filter(np.random.rand(64, 64, 20), 10) > 0.5
        )

        # Create and configure scene
        root = libcarna.node()
        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=500),
            local_transform=libcarna.translate(0, 0, 100),
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
        animation = libcarna.animate(
            libcarna.animate.rotate_local(camera),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class MIPStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. MIPStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2

        # Create and configure frame renderer
        mip = libcarna.mip(GEOMETRY_TYPE_VOLUME, cmap='jet')
        r = libcarna.renderer(800, 600, [mip])

        # Create volume
        np.random.seed(0)
        data = ndi.gaussian_filter(np.random.rand(64, 64, 20), 10)
        data = data - data.min()
        data = data / data.max()

        # Create and configure scene
        root = libcarna.node()
        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=500),
            local_transform=libcarna.translate(0, 0, 100),
        )
        # .. MIPStage: example-setup-end

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
        animation = libcarna.animate(
            libcarna.animate.rotate_local(camera),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class CuttingPlanesStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. CuttingPlanesStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2
        GEOMETRY_TYPE_PLANE = 3

        # Create and configure frame renderer
        cp = libcarna.cutting_planes(
            volume_geometry_type=GEOMETRY_TYPE_VOLUME,
            plane_geometry_type=GEOMETRY_TYPE_PLANE,
        )
        cp.windowing_level = 0.75
        cp.windowing_width = 0.5
        r = libcarna.renderer(800, 600, [cp])

        # Create volume
        np.random.seed(0)
        data = ndi.gaussian_filter(np.random.rand(64, 64, 20), 10)
        data = data - data.min()
        data = data / data.max()

        # Create and configure scene
        root = libcarna.node()
        volume = libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )
        zplane = libcarna.geometry(
            GEOMETRY_TYPE_PLANE,
            parent=volume,
            local_transform=libcarna.plane(
                normal=(0, 0, 1),
                distance=0,
            ),
        )
        for sign in (-1, +1):  # create left and right planes
            libcarna.geometry(
                GEOMETRY_TYPE_PLANE,
                parent=volume,
                local_transform=libcarna.plane(
                    normal=(1 * sign, 0, 0),
                    distance=63 / 2,
                ),
            )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=500),
            local_transform=libcarna.translate(0, 0, 100),
        )
        # .. CuttingPlanesStage: example-setup-end

        self.r, self.zplane, self.camera = r, zplane, camera

    def test(self):
        r, camera = self.r, self.camera

        # Render scene
        array = r.render(camera)

        # Verify result
        self.assert_image_almost_expected(array)

    def test__animated(self):
        r, zplane, camera = self.r, self.zplane, self.camera

        # .. CuttingPlanesStage: example-animation-start
        # Define animation
        animation = libcarna.animate(
            libcarna.animate.bounce_local(
                zplane,
                axis='z',
                amplitude=38 / 2,
            ),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))
        # .. CuttingPlanesStage: example-animation-end

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class DVRStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. DVRStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2

        # Create and configure frame renderer
        dvr = libcarna.dvr(
            GEOMETRY_TYPE_VOLUME, sr=800, transl=0.1, diffuse=0.8,
        )
        dvr.cmap.clear()
        dvr.cmap.write_linear_segment(
            0.7, 1.0,
            libcarna.color(0, 150, 255, 150),
            libcarna.color(255, 0, 255, 255),
        )
        r = libcarna.renderer(800, 600, [dvr])

        # Create volume
        np.random.seed(0)
        data = ndi.gaussian_filter(np.random.rand(64, 64, 20), 10)
        data = data - data.min()
        data = data / data.max()

        # Create and configure scene
        root = libcarna.node()
        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
            normals=True,
        )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=500),
            local_transform=libcarna.translate(0, 0, 100),
        )
        # .. DVRStage: example-setup-end

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
        animation = libcarna.animate(
            libcarna.animate.rotate_local(camera),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))

        # Verify result
        self.assert_image_almost_expected(np.array(frames))


class DRRStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. DRRStage: example-setup-start
        GEOMETRY_TYPE_VOLUME = 2

        # Create and configure frame renderer
        drr = libcarna.drr(
            GEOMETRY_TYPE_VOLUME, sr=800, inverse=True,
            lothres=0, upthres=1000, upmulti=3,
        )
        r = libcarna.renderer(
            800, 600, [drr], bgcolor=libcarna.color.WHITE_NO_ALPHA,
        )

        # Create volume
        np.random.seed(0)
        data = ndi.gaussian_filter(np.random.rand(64, 64, 20), 10)
        data = data - data.min()
        data = data / data.max()

        # Create and configure scene
        root = libcarna.node()
        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )
        camera = libcarna.camera(
            parent=root,
            projection=r.frustum(fov=90, z_near=1, z_far=500),
            local_transform=libcarna.translate(0, 0, 100),
        )
        # .. DRRStage: example-setup-end

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
        animation = libcarna.animate(
            libcarna.animate.rotate_local(camera),
            n_frames=50,
        )

        # Render animation
        frames = list(animation.render(r, camera))

        # Verify result
        self.assert_image_almost_expected(np.array(frames))
