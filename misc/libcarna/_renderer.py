from typing import Iterable

import numpy as np

import libcarna


class renderer:
    """
    Create a renderer, that conveniently combines a :class:`frame_renderer` and a :class:`surface`.

    Arguments:
        width: Horizontal rendering resolution.
        height: Vertical rendering resolution.
        stages: List of stages to be added to the frame renderer.
        ctx: OpenGL context to be used for rendering. If `None`, a new :class:`egl_context` will be created.
    """

    width: int
    """
    Horizontal rendering resolution.
    """

    height: int
    """
    Vertical rendering resolution.
    """

    def __init__(self, width: int, height: int, stages: Iterable[libcarna.base.RenderStage], ctx: libcarna.base.GLContext | None = None):
        if ctx is None:
            ctx = libcarna.egl_context()
        surface = libcarna.surface(ctx, width, height)
        frame_renderer = libcarna.frame_renderer(ctx, surface.width, surface.height)

        # Add stages to the frame renderer
        renderer_helper = None
        for stage in stages:
            if renderer_helper is None:
                renderer_helper = libcarna.frame_renderer_helper(frame_renderer)
            renderer_helper.add_stage(stage)
        if renderer_helper is not None:
            renderer_helper.commit()

        # Build method for rendering, that hides the frame renderer (so that it cannot be reshaped, because this would
        # require a new surface)
        def render(camera: libcarna.base.Camera, root: libcarna.base.Node | None = None) -> np.ndarray:
            surface.begin()
            frame_renderer.render(camera, root)
            return surface.end()

        # Build auxiliariy methods for projection matrices that fit the aspect ratio of the surface
        def frustum(fov: float, z_near: float, z_far: float):
            return libcarna.base.math.frustum(fov, height / width, z_near, z_far)

        self.render = render
        self.frustum = frustum
        self.width = width
        self.height = height

    def render(self, camera: libcarna.base.Camera, root: libcarna.base.Node | None = None) -> np.ndarray:
        """
        Render scene `root` from `camera` point of view to a NumPy array.
        """
        ...

    def frustum(self, fov: float, z_near: float, z_far: float) -> np.ndarray:
        """
        Create a projection matrix that is described by the frustum.
        
        Wrapper for :func:`libcarna.base.math.frustum` that ensures that the geometry of the frustum fits the aspect
        ratio of the surface of the renderer.
        """
        ...