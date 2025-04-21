import re

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


def _create_spatial_factory(spatial_type_name):
    spatial_type = getattr(carna.base, spatial_type_name)
    def spatial_factory(*args, parent=None, **kwargs):
        spatial = spatial_type(*args, **kwargs)
        if parent is not None:
            parent.attach_child(spatial)
        return spatial
    return spatial_factory


node = _create_spatial_factory('Node')
camera = _create_spatial_factory('Camera')


def geometry(geometry_type: int, tag: str = '', parent: carna.base.Node | None = None):
    class Geometry(carna.base.Geometry):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            super().put_feature(key, value)

    geometry = Geometry(geometry_type, tag)
    if parent is not None:
        parent.attach_child(geometry)
    return geometry


def material(shader_name: str, **kwargs):
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


_expand_module(carna.base)
_expand_module(carna.egl)
_expand_module(carna.presets)
_expand_module(carna.helpers)