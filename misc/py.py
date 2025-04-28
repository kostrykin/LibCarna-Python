import re
from typing import (
    Callable,
    Iterable,
    Literal,
    Sequence,
)

import numpy as np

import carna.base
import carna.egl
import carna.presets
import carna.helpers


AxisLiteral = Literal['x', 'y', 'z']
AxisHint = AxisLiteral | tuple[float, float, float] | list[float, float, float]


def _resolve_axis_hint(axis: AxisHint) -> tuple[float, float, float]:
    if isinstance(axis, str):
        match axis:
            case 'x':
                return (1, 0, 0)
            case 'y':
                return (0, 1, 0)
            case 'z':
                return (0, 0, 1)
            case _:
                raise ValueError(f'Invalid axis hint: {axis}')
    elif len(axis) == 3:
        return tuple(axis)
    else:
        raise ValueError(f'Invalid axis hint: {axis}')


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
        if target_name.endswith('_rendering_stage'):
            target_name = target_name.replace('_rendering_stage', '_renderer')
        if target_name in globals():
            continue

        # Skip blacklisted members
        if target_name.startswith('volume_grid_helper_'):
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
    def spatial_factory(tag: str | None = None, *, parent: carna.base.Node | None = None, **kwargs):
        """
        Create a spatial object of the given type.

        Arguments:
            tag: An arbitrary string, that helps identifying the object.
            parent: Parent node to attach the spatial to, or `None`.
            **kwargs: Attributes to be set on the newly created object.
        """
        spatial = spatial_type() if tag is None else spatial_type(tag)
        _setup_spatial(spatial, parent, **kwargs)
        return spatial
    return spatial_factory


node = _create_spatial_factory('Node')
camera = _create_spatial_factory('Camera')


def geometry(
        geometry_type: int,
        tag: str | None = None,
        *,
        parent: carna.base.Node | None = None,
        features: dict | None = None,
        **kwargs,
    ) -> carna.base.Geometry:
    """
    Create a :class:`carna.base.Geometry` object.

    Arguments:
        geometry_type: The type of the geometry.
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the spatial to, or `None`.
        **kwargs: Attributes to be set on the newly created object.
    """
    class Geometry(carna.base.Geometry):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            super().put_feature(key, value)

    geometry = Geometry(geometry_type) if tag is None else Geometry(geometry_type, tag)
    _setup_spatial(geometry, parent, **kwargs)
    for key, value in (features or dict()).items():
        geometry[key] = value
    return geometry


def material(shader_name: str, **kwargs) -> carna.base.Material:
    """
    Create a :class:`carna.base.Material` object.

    Arguments:
        shader_name: The shader to be used for rendering.
        **kwargs: Uniform shader parameters.
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

        # Build method for rendering, that hides the frame renderer (so that it cannot be reshaped, because this would
        # require a new surface)
        def render(camera: carna.base.Camera, root: carna.base.Node | None = None) -> np.ndarray:
            surface.begin()
            frame_renderer.render(camera, root)
            return surface.end()

        # Build auxiliariy methods for projection matrices that fit the aspect ratio of the surface
        def frustum(fov: float, z_near: float, z_far: float):
            return carna.base.math.frustum(fov, height / width, z_near, z_far)

        self.render = render
        self.frustum = frustum
        self.width = width
        self.height = height

    def render(self, camera: carna.base.Camera, root: carna.base.Node | None = None) -> np.ndarray:
        """
        Render scene `root` from `camera` point of view to a NumPy array.
        """
        ...

    def frustum(self, fov: float, z_near: float, z_far: float) -> np.ndarray:
        """
        Create a projection matrix that is described by the frustum.
        
        Wrapper for :func:`carna.base.math.frustum` that ensures that the geometry of the frustum fits the aspect ratio
        of the surface of the renderer.
        """
        ...


class animation:
    """
    Create an animation that can be rendered.

    Arguments:
        step_functions: List of function that are called for each frame of the animation. Each function is called with
            a single argument `t`, which is a float in the range [0, 1]. The function should modify the scene in place.
            To obtain a smooth eternal animation, the scene should be in it's initial state at `t=1`.
        n_frames: Number of frames to be rendered.
    """

    def __init__(self, step_functions: list[Callable[[float], None]], n_frames: int = 25):
        self.step_functions = step_functions
        self.n_frames = n_frames

    def render(self, r: renderer, *args, **kwargs) -> Iterable[np.ndarray]:
        for t in np.linspace(1, 0, num=self.n_frames, endpoint=False)[::-1]:
            for step in self.step_functions:
                step(t)
            yield r.render(*args, **kwargs)

    @staticmethod
    def rotate_local(spatial: carna.base.Spatial, axis: AxisHint = 'y') -> Callable[[float], None]:
        """
        Create a step function for rotating an object's local coordinate system.
        """
        base_transform = spatial.local_transform
        axis = _resolve_axis_hint(axis)
        def step(t: float):
            spatial.local_transform = carna.math.rotation(axis, radians=2 * np.pi * t) @ base_transform
        return step


def volume(
        geometry_type: int,
        array: np.ndarray,
        tag: str | None = None,
        *,
        parent: carna.base.Node | None = None,
        normals: bool = False,
        spacing: np.ndarray | None = None,
        dimensions: np.ndarray | None = None,
    ) -> carna.base.Node:
    """
    Create a renderable representation of 3D data using the specified `geometry_type`, that can be put anywhere in the
    scene graph. The 3D volume is centered in the returned node.

    Arguments:
        geometry_type: The type of the geometry.
        array: 3D data to be rendered.
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the volume to, or `None`.
        normals: Governs normal mapping (if `True`, the 3D normal map will be pre-computed for the volume).
        spacing: Specifies the spacing between two adjacent voxel centers. Mutually exclusive with `dimensions`.
        dimensions: Specifies the spatial size of the whole volume. Mutually exclusive with `spacing`.
    """
    assert array.ndim == 3, 'Array must be 3D data.'
    assert (spacing is None) != (dimensions is None), 'Either spacing or dimensions must be provided.'

    # Choose appropriate intensity component and prepare the data for loading (data is always transferred as float)
    if array.dtype == np.uint8:
        intensity_component = 'IntensityVolumeUInt8'
        array = array / 0xff
    elif array.dtype == np.bool:
        intensity_component = 'IntensityVolumeUInt8'
    elif array.dtype == np.uint16:
        intensity_component = 'IntensityVolumeUInt16'
        array = array / 0xffff
    elif np.issubdtype(array.dtype, np.floating):
        intensity_component = 'IntensityVolumeUInt16'
    else:
        raise ValueError(f'Unsupported data type: {array.dtype}')
    
    # Choose appropriate buffer type
    if normals:
        helper_type_name = f'VolumeGridHelper_{intensity_component}_NormalMap3DInt8'
    else:
        helper_type_name = f'VolumeGridHelper_{intensity_component}'
    
    # Create the buffer and load the data
    volume_type = getattr(carna.helpers, helper_type_name)
    helper = volume_type(native_resolution=array.shape)
    helper.load_intensities(array)

    # Deduce the parameters for spacing and dimensions
    create_node_kwargs = dict()
    if spacing is not None:
        create_node_kwargs['spacing'] = volume_type.Spacing(spacing)
    if dimensions is not None:
        create_node_kwargs['dimensions'] = volume_type.Dimensions(spacing)

    # Create a wrapper node, so that it is safe to modify the `.local_transform` property (making such modifications
    # directly to the property of the node created by the wrapper is discouraged in the docs)
    # https://kostrykin.github.io/Carna/html/classCarna_1_1helpers_1_1VolumeGridHelper.html#ab03947088a1de662b7a468516e4b5e24
    wrapper_node = carna.base.Node(tag) if tag is not None else carna.base.Node()
    _setup_spatial(wrapper_node, parent)

    # Create volume node
    volume_node = helper.create_node(geometry_type=geometry_type, **create_node_kwargs)
    wrapper_node.attach_child(volume_node)
    return volume_node


_expand_module(carna.base)
_expand_module(carna.egl)
_expand_module(carna.presets)
_expand_module(carna.helpers)