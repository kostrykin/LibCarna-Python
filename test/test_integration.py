import numpy as np

import libcarna
import testsuite


class VolumeGridHelper_IntensityVolumeUInt16(testsuite.LibCarnaTestCase):

    def test(self):
        data = libcarna.data.toy()
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
        opaque_renderer = libcarna.opaque_renderer(0)
        self.frame_renderer.append_stage(opaque_renderer)

    def test__render(self):
        opaque_renderer = libcarna.opaque_renderer(0)
        self.frame_renderer.append_stage(opaque_renderer)
        root = libcarna.node()
        camera = libcarna.camera()
        root.attach_child(camera)
        self.frame_renderer.render(camera)


class OpaqueRenderingStage(testsuite.LibCarnaRenderingTestCase):

    def setUp(self):
        # .. OpaqueRenderingStage: example-setup-start
        GEOMETRY_TYPE_OPAQUE = 1

        # Create mesh
        box = libcarna.meshes.create_box(40, 40, 40)

        # Create scene
        root = libcarna.node()

        libcarna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            mesh=box,
            material=libcarna.material('solid', color='#ff0000'),
        ).translate(-10, -10, -40)

        libcarna.geometry(
            GEOMETRY_TYPE_OPAQUE,
            parent=root,
            mesh=box,
            material=libcarna.material('solid', color='#00ff00'),
        ).translate(+10, +10, +40)

        camera = libcarna.camera(
            parent=root,
        ).frustum(fov=90, z_near=1, z_far=1e3).translate(0, 0, 250)

        # Create renderer
        r = libcarna.renderer(800, 600, [
                libcarna.opaque_renderer(GEOMETRY_TYPE_OPAQUE),
            ]
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

        # Create volume
        data = (libcarna.data.toy() > 0.68)

        # Create scene
        root = libcarna.node()

        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )

        camera = libcarna.camera(
            parent=root,
        ).frustum(fov=90, z_near=1, z_far=500).translate(0, 0, 100)

        # Create renderer
        r = libcarna.renderer(800, 600, [
                libcarna.mask_renderer(GEOMETRY_TYPE_VOLUME),
            ]
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

        # Create data
        data = libcarna.data.toy()

        # Create scene
        root = libcarna.node()

        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )

        camera = libcarna.camera(
            parent=root,
        ).frustum(fov=90, z_near=1, z_far=500).translate(0, 0, 100)

        # Create renderer
        r = libcarna.renderer(800, 600, [
                libcarna.mip(GEOMETRY_TYPE_VOLUME, cmap='jet'),
            ]
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

        # Create volume
        data = libcarna.data.toy()

        # Create scene
        root = libcarna.node()

        volume = libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )

        zplane = libcarna.geometry(  # create z-plane
            GEOMETRY_TYPE_PLANE,
            parent=volume,
        ).plane(normal='z', distance=0)

        for axis in ('-x', '+x'):  # create left and right planes
            libcarna.geometry(
                GEOMETRY_TYPE_PLANE,
                parent=volume,
            ).plane(normal=axis, distance=volume.extent[0] / 2)

        camera = libcarna.camera(
            parent=root,
        ).frustum(fov=90, z_near=1, z_far=500).translate(0, 0, 100)

        # Create renderer
        r = libcarna.renderer(800, 600, [
                libcarna.cutting_planes(
                    volume_geometry_type=GEOMETRY_TYPE_VOLUME,
                    plane_geometry_type=GEOMETRY_TYPE_PLANE,
                    clim=(0.5, 1),
                ),
            ]
        )
        # .. CuttingPlanesStage: example-setup-end

        self.r, self.volume, self.zplane, self.camera = r, volume, zplane, camera

    def test(self):
        r, camera = self.r, self.camera

        # Render scene
        array = r.render(camera)

        # Verify result
        self.assert_image_almost_expected(array)

    def test__animated(self):
        r, volume, zplane, camera = self.r, self.volume, self.zplane, self.camera

        # .. CuttingPlanesStage: example-animation-start
        # Define animation
        animation = libcarna.animate(
            libcarna.animate.bounce_local(
                zplane,
                axis='z',
                amplitude=volume.extent[2] / 2,
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

        # Create volume
        data = libcarna.data.toy()

        # Create scene
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
        ).frustum(fov=90, z_near=1, z_far=500).translate(0, 0, 100)

        # Create renderer
        dvr = libcarna.dvr(
            GEOMETRY_TYPE_VOLUME, sr=800, transl=0.1, diffuse=0.8,
        )
        dvr.cmap.clear()
        dvr.cmap.linear_segment(
            0.7, 1.0,
            libcarna.color(0, 150, 255, 150),
            libcarna.color(255, 0, 255, 255),
        )
        r = libcarna.renderer(800, 600, [dvr])
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

        # Create volume
        data = libcarna.data.toy()

        # Create scene
        root = libcarna.node()

        libcarna.volume(
            GEOMETRY_TYPE_VOLUME,
            data,
            parent=root,
            spacing=(1, 1, 2),
        )

        camera = libcarna.camera(
            parent=root,
        ).frustum(fov=90, z_near=1, z_far=500).translate(0, 0, 100)

        # Create renderer
        r = libcarna.renderer(
            800, 600, [
                libcarna.drr(
                    GEOMETRY_TYPE_VOLUME, sr=800, inverse=True,
                    lothres=0, upthres=1000, upmulti=3,
                ),
            ],
            bgcolor=libcarna.color.WHITE_NO_ALPHA,
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
