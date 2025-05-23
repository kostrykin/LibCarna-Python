import numpy as np

import libcarna
from ._alias import kwalias
from ._axes import AxisHint, resolve_axis_hint
from ._transform import transform
from ._typing import (
    Literal,
    Self,
)


def _transform_into_local(target: libcarna.base.Spatial, rhs: libcarna.base.Spatial) -> np.ndarray:
    """
    Compute the transformation from the local coordinate system of a spatial object `rhs` into the local coordinate
    system of another spatial object `target`.
    """
    if target is rhs:
        return transform(np.eye(4))
    else:
        return transform(np.linalg.inv(target.world_transform) @ rhs.world_transform)
    

class _spatial_mixin:

    @kwalias('degrees', 'deg')
    @staticmethod
    def rotation(axis: AxisHint, degrees: float) -> np.ndarray:
        axis = resolve_axis_hint(axis)
        return libcarna.base.math.rotation(axis, radians=libcarna.base.math.deg2rad(degrees))
    
    @staticmethod
    def scaling(*factors: float) -> np.ndarray:
        if len(factors) == 1:
            factors = (factors[0], factors[0], factors[0])
        elif len(factors) != 3:
            raise ValueError('Scale factor must be a single value, or a tuple of three values.')
        return libcarna.base.math.scaling(*factors)
    
    @staticmethod
    def translation(x: float = 0, y: float = 0, z: float = 0) -> np.ndarray:
        return libcarna.base.math.translation(x, y, z)
    
    def rotate_local(self, *args, **kwargs) -> Self:
        """
        Rotate the local coordinate system of this spatial object.

        Arguments:
            axis: The axis of rotation. Can be 'x', 'y', 'z', or an arbitrary axis (vector with 3 components).
            degrees: The angle of rotation in degrees (alias: `deg`).
        """
        self.local_transform = _spatial_mixin.rotation(*args, **kwargs) @ self.local_transform
        return self
    
    def scale_local(self, *args, **kwargs) -> Self:
        """
        Scale the local coordinate system of this spatial object.

        Arguments:
            factors: The scale factors for the x, y, and z axes. If a single value is provided, it is used for all
                three axes.
        """
        self.local_transform = _spatial_mixin.scaling(*args, **kwargs) @ self.local_transform
        return self
    
    def translate_local(self, *args, **kwargs) -> Self:
        """
        Translate the local coordinate system of this spatial object.

        Arguments:
            x: The translation along the x-axis.
            y: The translation along the y-axis.
            z: The translation along the z-axis.
        """
        self.local_transform = self.local_transform @ _spatial_mixin.translation(*args, **kwargs)
        return self
    
    def rotate(self, *args, **kwargs) -> Self:
        """
        Rotate this spatial object in its local coordinate system.

        Arguments:
            axis: The axis of rotation. Can be 'x', 'y', 'z', or an arbitrary axis (vector with 3 components).
            degrees: The angle of rotation in degrees (alias: `deg`).
        """
        self.local_transform = self.local_transform @ _spatial_mixin.rotation(*args, **kwargs)
        return self
    
    def scale(self, *args, **kwargs) -> Self:
        """
        Scale this spatial object in its local coordinate system.

        Arguments:
            factors: The scale factors for the x, y, and z axes. If a single value is provided, it is used for all
                three axes.
        """
        self.local_transform = self.local_transform @ _spatial_mixin.scaling(*args, **kwargs)
        return self
    
    def translate(self, *args, **kwargs) -> Self:
        """
        Translate this spatial object in its local coordinate system.

        Arguments:
            x: The translation along the x-axis.
            y: The translation along the y-axis.
            z: The translation along the z-axis.
        """
        self.local_transform = _spatial_mixin.translation(*args, **kwargs) @ self.local_transform
        return self
    
    @kwalias('distance', 'dist', 'd')
    def plane(self, normal: AxisHint, distance: float) -> Self:
        normal = resolve_axis_hint(normal)
        self.local_transform = libcarna.base.math.plane(normal=normal, distance=distance) @ self.local_transform
        return self
    
    def transform_from(self, rhs: libcarna.base.Spatial) -> np.ndarray:
        """
        Compute the transformation from the local coordinate system of a spatial object `rhs` into the local coordinate
        system of this spatial object.
        """
        return _transform_into_local(self, rhs)


def _setup_spatial(spatial, parent: libcarna.base.Node | None = None, **kwargs):
    if parent is not None:
        parent.attach_child(spatial)
    for key, value in kwargs.items():

        # If value is not a `np.ndarray`, check whether it has a `mat` attribute and if it is a `np.ndarray`
        if (
            key == 'local_transform' and
            not isinstance(value, np.ndarray) and
            hasattr(value, 'mat') and
            isinstance(value.mat, np.ndarray)
        ):
            value = value.mat
            
        setattr(spatial, key, value)


def node(tag: str | None = None, *, parent: libcarna.base.Node | None = None, **kwargs) -> libcarna.base.Node:
    """
    Create a :class:`carna.base.Node` object, that other spatial objects can be added to.

    Arguments:
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the spatial to, or `None`.
        **kwargs: Attributes to be set on the newly created object.
    """
    class Node(libcarna.base.Node, _spatial_mixin):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    node = Node() if tag is None else Node(tag)
    _setup_spatial(node, parent, **kwargs)
    return node


def camera(tag: str | None = None, *, parent: libcarna.base.Node | None = None, **kwargs) -> libcarna.base.Camera:
    """
    Create a :class:`carna.base.Camera` object.

    Arguments:
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the spatial to, or `None`.
        **kwargs: Attributes to be set on the newly created object.
    """
    class Camera(libcarna.base.Camera, _spatial_mixin):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def proj(self, projection: np.ndarray | Literal['frustum'], **kwargs) -> Self:
            """
            Set the projection matrix of the camera.
            """
            if isinstance(projection, np.ndarray):
                self.projection = projection
                self.update_projection = lambda *args, **kwargs: None

            elif isinstance(projection, str) and projection == 'frustum':
                fov_rad = libcarna.base.math.deg2rad(kwargs['fov'])
                z_near = kwargs['z_near']
                z_far = kwargs['z_far']

                def update_projection(width: int, height: int):
                    self.projection = libcarna.base.math.frustum(fov_rad, height / width, z_near, z_far)

                self.update_projection = update_projection

            else:
                raise ValueError(f'Unsupported projection type: {projection}')
            return self

        def frustum(self, fov: float, z_near: float, z_far: float) -> Self:
            """
            Set a projection matrix that is described by the frustum.
            
            Wrapper for :func:`libcarna.base.math.frustum` that ensures that the geometry of the frustum fits the
            aspect ratio of the renderer.

            Arguments:
                fov: Field of view in degrees.
                z_near: Near clipping plane.
                z_far: Far clipping plane.
            """
            return self.proj('frustum', fov=fov, z_near=z_near, z_far=z_far)

    camera = Camera() if tag is None else Camera(tag)
    _setup_spatial(camera, parent, **kwargs)
    return camera


def geometry(
        geometry_type: int,
        tag: str | None = None,
        *,
        parent: libcarna.base.Node | None = None,
        mesh: libcarna.base.GeometryFeature | None = None,
        material: libcarna.base.Material | None = None,
        **kwargs,
    ) -> libcarna.base.Geometry:
    """
    Create a :class:`carna.base.Geometry` object.

    Arguments:
        geometry_type: The type of the geometry.
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the spatial to, or `None`.
        mesh: A mesh to be attached to this geometry object.
        material: A material to be attached to this geometry object.
        **kwargs: Attributes to be set on the newly created object.
    """
    class Geometry(libcarna.base.Geometry, _spatial_mixin):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    geometry = Geometry(geometry_type) if tag is None else Geometry(geometry_type, tag)
    _setup_spatial(geometry, parent, **kwargs)
    if mesh is not None:
        geometry.put_feature(libcarna.mesh_renderer.DEFAULT_ROLE_MESH, mesh)
    if material is not None:
        geometry.put_feature(libcarna.mesh_renderer.DEFAULT_ROLE_MATERIAL, material)
    return geometry


def volume(
        geometry_type: int,
        array: np.ndarray,
        tag: str | None = None,
        *,
        units: Literal['raw', 'hu'] = 'raw',
        parent: libcarna.base.Node | None = None,
        normals: bool = False,
        spacing: np.ndarray | None = None,
        extent: np.ndarray | None = None,
        **kwargs,
    ) -> libcarna.base.Node:
    """
    Create a renderable representation of 3D data using the specified `geometry_type`, that can be put anywhere in the
    scene graph. The 3D volume is centered in the returned node.

    Arguments:
        geometry_type: The type of the geometry.
        array: 3D data to be rendered.
        tag: An arbitrary string, that helps identifying the created node.
        units: The units of the data. If `'hu'`, the data is assumed to be in Hounsfield Units (HU).
        parent: Parent node to attach the volume to, or `None`.
        normals: Governs normal mapping (if `True`, the 3D normal map will be pre-computed for the volume).
        spacing: Specifies the spacing between two adjacent voxel centers. Mutually exclusive with `extent`.
        extent: Specifies the spatial size of the whole volume. Mutually exclusive with `spacing`.
        **kwargs: Attributes to be set on the created node.
    """
    assert array.ndim == 3, 'Array must be 3D data.'
    assert (spacing is None) != (extent is None), 'Either spacing or extent must be provided.'
    assert np.isnan(array).sum() == 0, 'Array must not contain NaN values.'
    assert np.isinf(array).sum() == 0, 'Array must not contain inf values.'

    # Preprocess the data based on the units
    array_dtype = array.dtype
    match units:
        case 'hu':
            raw2norm = lambda array: (array + 1024) / 4095
            norm2raw = lambda array: (array * 4095) - 1024
            array = array.clip(-1024, +3071)
        case 'raw':
            array_offset = float(array.min())
            array_factor = float(array.max() - array_offset)
            if array_factor > 0:
                raw2norm = lambda array: (array - array_offset) / array_factor
                norm2raw = lambda array: (array * array_factor) + array_offset
            else:
                raw2norm = lambda array: np.full(fill_value=0, shape=array.shape, dtype=np.uint8)
                norm2raw = lambda array: np.full(fill_value=array_offset, shape=array.shape, dtype=array_dtype)
        case _:
            raise ValueError(f'Unsupported units: "{units}"')
    array = raw2norm(array)

    # Choose appropriate intensity component
    if array.dtype == np.uint8:
        intensity_component = 'IntensityVolumeUInt8'
    elif array.dtype == bool:
        intensity_component = 'IntensityVolumeUInt8'
    elif array.dtype == np.uint16:
        intensity_component = 'IntensityVolumeUInt16'
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
    volume_type = getattr(libcarna.helpers, helper_type_name)
    helper = volume_type(native_resolution=array.shape)
    helper.load_intensities(array)

    # Deduce the parameters for spacing and extent
    create_node_kwargs = dict()
    if spacing is not None:
        create_node_kwargs['spacing'] = volume_type.Spacing(spacing)
        extent = np.subtract(array.shape, 1) * spacing
    elif extent is not None:
        create_node_kwargs['extent'] = volume_type.Extent(extent)
        spacing = np.divide(extent, np.subtract(array.shape, 1))

    # Create a wrapper node, so that it is safe to modify the `.local_transform` property (making such modifications
    # directly to the property of the node created by the wrapper is discouraged in the docs)
    # https://kostrykin.github.io/LibCarna/html/classLibCarna_1_1helpers_1_1VolumeGridHelper.html#ab03947088a1de662b7a468516e4b5e24
    class WrapperNode(libcarna.base.Node, _spatial_mixin):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.extent  = extent
            self.spacing = spacing

        def transform_into_voxels_from(self, rhs: libcarna.base.Spatial) -> np.ndarray:
            """
            Compute the transformation from the local coordinate system of a spatial object `rhs` into the voxel
            coordinate system of this volume.
            """
            return transform(
                libcarna.base.math.scaling(np.subtract(array.shape, 1) / extent) @
                libcarna.base.math.translation(extent / 2) @
                self.transform_from(rhs).mat
            )
        
        def transform_from_voxels_into(self, lhs: libcarna.base.Spatial) -> np.ndarray:
            """
            Compute the transformation from the voxel coordinate system of this volume into the local coordinate system
            of a spatial object `lhs`.
            """
            return transform(np.linalg.inv(self.transform_into_voxels_from(lhs).mat))
        
        def normalized(self, array: np.ndarray) -> np.ndarray:
            """
            Convert raw array intensities to the normalized intensities in [0, 1] used for rendering.
            """
            return raw2norm(np.asarray(array))

        def raw(self, array: np.ndarray) -> np.ndarray:
            """
            Convert normalized intensities in [0, 1] used for rendering to the raw array intensities.
            """
            return norm2raw(np.asarray(array)).astype(array_dtype)

    wrapper_node = WrapperNode(tag) if tag is not None else WrapperNode()
    _setup_spatial(wrapper_node, parent, **kwargs)

    # Create volume node
    volume_node = helper.create_node(geometry_type=geometry_type, **create_node_kwargs)
    wrapper_node.attach_child(volume_node)
    return wrapper_node
