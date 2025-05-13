from typing import Iterable

import numpy as np

import libcarna
from ._alias import kwalias


class renderer:
    """
    Create a renderer, that conveniently combines a :class:`frame_renderer` and a :class:`surface`.

    Arguments:
        width: Horizontal rendering resolution.
        height: Vertical rendering resolution.
        stages: List of stages to be added to the frame renderer.
        background_color: Background color of the surface (aliases: `bgcolor`, `bgc`).
        gl_context: OpenGL context to be used for rendering (alias: `ctx`). If `None`, a new :class:`egl_context` will
            be created.
    """

    width: int
    """
    Horizontal rendering resolution.
    """

    height: int
    """
    Vertical rendering resolution.
    """

    gl_context: libcarna.gl_context
    """
    OpenGL context used for rendering.
    """

    @kwalias('background_color', 'bgcolor', 'bgc')
    @kwalias('gl_context', 'ctx')
    def __init__(
            self,
            width: int,
            height: int,
            stages: Iterable[libcarna.base.RenderStage],
            background_color: libcarna.color = libcarna.color.BLACK_NO_ALPHA,
            gl_context: libcarna.gl_context | None = None,
        ):
        self.gl_context = gl_context or libcarna.egl_context()
        surface = libcarna.surface(self.gl_context, width, height)
        frame_renderer = libcarna.frame_renderer(self.gl_context, surface.width, surface.height)
        frame_renderer.set_background_color(background_color)

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
            if hasattr(camera, 'update_projection'):
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
