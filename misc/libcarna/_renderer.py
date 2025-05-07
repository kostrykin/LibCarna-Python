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
        bgcolor: Background color of the surface.
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

    def __init__(
            self,
            width: int,
            height: int,
            stages: Iterable[libcarna.base.RenderStage],
            bgcolor: libcarna.color = libcarna.color.BLACK_NO_ALPHA,
            ctx: libcarna.base.GLContext | None = None,
        ):
        if ctx is None:
            ctx = libcarna.egl_context()
        surface = libcarna.surface(ctx, width, height)
        frame_renderer = libcarna.frame_renderer(ctx, surface.width, surface.height)
        frame_renderer.set_background_color(bgcolor)

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

            # Update camera projection matrix to fit the aspect ratio of the surface
            if isinstance(camera, libcarna.camera):
                camera.update_projection(surface.width, surface.height)

            # Perform the rendering
            surface.begin()
            frame_renderer.render(camera, root)
            return surface.end()

        self.render = render
        self.width = width
        self.height = height

    def render(self, camera: libcarna.base.Camera, root: libcarna.base.Node | None = None) -> np.ndarray:
        """
        Render scene `root` from `camera` point of view to a NumPy array.
        """
        ...
