import re

import libcarna.base
import libcarna.egl
import libcarna.presets
import libcarna.helpers


def _camel_to_snake(name):
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _strip_suffix(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def _expand_module(module):
    for member_name in dir(module):

        # Skip private members
        if member_name.startswith('_'):
            continue

        # Resolve target name
        target_name = _camel_to_snake(member_name)
        target_name = target_name.replace('lib_carna', 'libcarna')
        if target_name == 'mask_rendering_stage':
            target_name = 'mask_renderer'
        elif target_name == 'mesh_factory':
            target_name = 'meshes'
        else:
            target_name = _strip_suffix(target_name, '_rendering_stage')
        target_name = _strip_suffix(target_name, '_stage')

        # Skip if the target already exists
        if target_name in globals():
            continue

        # Skip blacklisted members
        if target_name.startswith('volume_grid_helper_'):
            continue

        # Populate the global namespace with the member
        member = getattr(module, member_name)
        globals()[target_name] = member


_expand_module(libcarna.base)
_expand_module(libcarna.egl)
_expand_module(libcarna.presets)
_expand_module(libcarna.helpers)
