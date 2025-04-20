import numpy as np

import carna
import carna.egl
import testsuite


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
