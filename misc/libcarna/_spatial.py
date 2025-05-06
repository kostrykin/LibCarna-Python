from typing import Literal

import numpy as np

import libcarna
from libcarna._transform import transform as _transform


def _transform_into_local(target: libcarna.base.Spatial, rhs: libcarna.base.Spatial) -> np.array:
    """
    Compute the transformation from the local coordinate system of a spatial object `rhs` into the local coordinate
    system of another spatial object `target`.
    """
    if target is rhs:
        return _transform(np.eye(4))
    else:
        return _transform(np.linalg.inv(target.world_transform) @ rhs.world_transform)
    

class _spatial_mixin:
    
    def transform_from(self, rhs: libcarna.base.Spatial) -> np.array:
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

    camera = Camera() if tag is None else Camera(tag)
    _setup_spatial(camera, parent, **kwargs)
    return camera


def geometry(
        geometry_type: int,
        tag: str | None = None,
        *,
        parent: libcarna.base.Node | None = None,
        features: dict | None = None,
        **kwargs,
    ) -> libcarna.base.Geometry:
    """
    Create a :class:`carna.base.Geometry` object.

    Arguments:
        geometry_type: The type of the geometry.
        tag: An arbitrary string, that helps identifying the object.
        parent: Parent node to attach the spatial to, or `None`.
        **kwargs: Attributes to be set on the newly created object.
    """
    class Geometry(libcarna.base.Geometry, _spatial_mixin):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            super().put_feature(key, value)

    geometry = Geometry(geometry_type) if tag is None else Geometry(geometry_type, tag)
    _setup_spatial(geometry, parent, **kwargs)
    for key, value in (features or dict()).items():
        geometry[key] = value
    return geometry


def volume(
        geometry_type: int,
        array: np.ndarray,
        tag: str | None = None,
        *,
        units: Literal['raw', 'huv'] = 'raw',
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
        units: The units of the data. If `'huv'`, the data is assumed to be in Hounsfield Units (HU).
        parent: Parent node to attach the volume to, or `None`.
        normals: Governs normal mapping (if `True`, the 3D normal map will be pre-computed for the volume).
        spacing: Specifies the spacing between two adjacent voxel centers. Mutually exclusive with `extent`.
        extent: Specifies the spatial size of the whole volume. Mutually exclusive with `spacing`.
        **kwargs: Attributes to be set on the created node.
    """
    assert array.ndim == 3, 'Array must be 3D data.'
    assert (spacing is None) != (extent is None), 'Either spacing or extent must be provided.'

    # Preprocess the data based on the units
    match units:
        case 'huv':
            array = (array.clip(-1024, +3071) + 1024) / 4095
        case 'raw':
            pass
        case _:
            raise ValueError(f'Unsupported units: "{units}"')

    # Choose appropriate intensity component and prepare the data for loading (data is always transferred as float)
    if array.dtype == np.uint8:
        intensity_component = 'IntensityVolumeUInt8'
        array = array / 0xff
    elif array.dtype == bool:
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

    # Create a wrapper node, so that it is safe to modify the `.local_transform` property (making such modifications
    # directly to the property of the node created by the wrapper is discouraged in the docs)
    # https://kostrykin.github.io/LibCarna/html/classLibCarna_1_1helpers_1_1VolumeGridHelper.html#ab03947088a1de662b7a468516e4b5e24
    class WrapperNode(libcarna.base.Node, _spatial_mixin):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def transform_into_voxels_from(self, rhs: libcarna.base.Spatial) -> np.array:
            """
            Compute the transformation from the local coordinate system of a spatial object `rhs` into the voxel
            coordinate system of this volume.
            """
            return _transform(
                libcarna.base.math.scaling(np.subtract(array.shape, 1) / extent) @
                libcarna.base.math.translation(extent / 2) @
                self.transform_from(rhs).mat
            )

    wrapper_node = WrapperNode(tag) if tag is not None else WrapperNode()
    _setup_spatial(wrapper_node, parent, **kwargs)

    # Create volume node
    volume_node = helper.create_node(geometry_type=geometry_type, **create_node_kwargs)
    wrapper_node.attach_child(volume_node)
    return wrapper_node
