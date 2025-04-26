import re
from typing import Iterable

import numpy as np

import carna.base
import carna.egl
import carna.presets
import carna.helpers


def _camel_to_snake(name):
    
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _expand_module(module):
    for member_name in dir(module):

        # Skip private members
        if member_name.startswith('_'):
            continue

        # Skip if the target already exists
        target_name = _camel_to_snake(member_name)
        if target_name in globals():
            continue

        # Populate the global namespace with the member
        member = getattr(module, member_name)
        globals()[target_name] = member


def _setup_spatial(spatial, parent: carna.base.Node | None = None, **kwargs):
    if parent is not None:
        parent.attach_child(spatial)
    for key, value in kwargs.items():
        setattr(spatial, key, value)


def _create_spatial_factory(spatial_type_name):
    spatial_type = getattr(carna.base, spatial_type_name)
    def spatial_factory(*args, parent: carna.base.Node | None = None, **kwargs):
        f"""
        Create a {spatial_type_name} object.
        """
        spatial = spatial_type(*args)
        _setup_spatial(spatial, parent, **kwargs)
        return spatial
    return spatial_factory


node = _create_spatial_factory('Node')
camera = _create_spatial_factory('Camera')


def geometry(geometry_type: int, *args, parent: carna.base.Node | None = None, features: dict | None = None, **kwargs):
    """
    Create a :class:`carna.base.Geometry` object.
    """
    class Geometry(carna.base.Geometry):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            super().put_feature(key, value)

    geometry = Geometry(geometry_type, *args)
    _setup_spatial(geometry, parent, **kwargs)
    for key, value in (features or dict()).items():
        geometry[key] = value
    return geometry


def material(shader_name: str, **kwargs):
    """
    Create a :class:`carna.base.Material` object.
    """
    class Material(carna.base.Material):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            if shader_name in ('unshaded', 'solid') and (not hasattr(value, '__len__') or len(value) != 4):
                raise ValueError(f'Material "{shader_name}" requires a color value with 4 components (RGBA).')
            super().__setitem__(key, value)

    material = Material(shader_name)
    for key, value in kwargs.items():
        material[key] = value
    return material


class renderer:
    """
    Creates a renderer, that conveniently combines a :class:`frame_renderer` and a :class:`surface`.

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

    def __init__(self, width: int, height: int, stages: Iterable[carna.base.RenderStage], ctx: carna.base.GLContext | None = None):
        if ctx is None:
            ctx = carna.egl_context()
        surface = carna.surface(ctx, width, height)
        frame_renderer = carna.frame_renderer(ctx, surface.width, surface.height)

        # Add stages to the frame renderer
        renderer_helper = None
        for stage in stages:
            if renderer_helper is None:
                renderer_helper = carna.frame_renderer_helper(frame_renderer)
            renderer_helper.add_stage(stage)
        if renderer_helper is not None:
            renderer_helper.commit()

        # Build method that hides the frame renderer (so that it cannot be reshaped, because this would require a new surface)
        def render(camera: carna.base.Camera, root: carna.base.Node | None = None) -> np.ndarray:
            surface.begin()
            frame_renderer.render(camera, root)
            return surface.end()

        self.render = render
        self.width = width
        self.height = height

    def render(self, camera: carna.base.Camera, root: carna.base.Node | None = None) -> np.ndarray:
        """
        Renders scene `root` from `camera` point of view to a NumPy array.
        """
        ...


_expand_module(carna.base)
_expand_module(carna.egl)
_expand_module(carna.presets)
_expand_module(carna.helpers)