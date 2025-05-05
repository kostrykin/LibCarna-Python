import numpy as np

import libcarna


def _setup_spatial(spatial, parent: libcarna.base.Node | None = None, **kwargs):
    if parent is not None:
        parent.attach_child(spatial)
    for key, value in kwargs.items():
        setattr(spatial, key, value)


def _create_spatial_factory(spatial_type_name):
    spatial_type = getattr(libcarna.base, spatial_type_name)
    def spatial_factory(tag: str | None = None, *, parent: libcarna.base.Node | None = None, **kwargs):
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
    class Geometry(libcarna.base.Geometry):

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
        parent: Parent node to attach the volume to, or `None`.
        normals: Governs normal mapping (if `True`, the 3D normal map will be pre-computed for the volume).
        spacing: Specifies the spacing between two adjacent voxel centers. Mutually exclusive with `extent`.
        extent: Specifies the spatial size of the whole volume. Mutually exclusive with `spacing`.
        **kwargs: Attributes to be set on the created node.
    """
    assert array.ndim == 3, 'Array must be 3D data.'
    assert (spacing is None) != (extent is None), 'Either spacing or extent must be provided.'

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
    volume_type = getattr(libcarna.helpers, helper_type_name)
    helper = volume_type(native_resolution=array.shape)
    helper.load_intensities(array)

    # Deduce the parameters for spacing and extent
    create_node_kwargs = dict()
    if spacing is not None:
        create_node_kwargs['spacing'] = volume_type.Spacing(spacing)
    if extent is not None:
        create_node_kwargs['extent'] = volume_type.Extent(extent)

    # Create a wrapper node, so that it is safe to modify the `.local_transform` property (making such modifications
    # directly to the property of the node created by the wrapper is discouraged in the docs)
    # https://kostrykin.github.io/LibCarna/html/classLibCarna_1_1helpers_1_1VolumeGridHelper.html#ab03947088a1de662b7a468516e4b5e24
    wrapper_node = libcarna.base.Node(tag) if tag is not None else libcarna.base.Node()
    _setup_spatial(wrapper_node, parent, **kwargs)

    # Create volume node
    volume_node = helper.create_node(geometry_type=geometry_type, **create_node_kwargs)
    wrapper_node.attach_child(volume_node)
    return volume_node
