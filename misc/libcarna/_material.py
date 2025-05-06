import libcarna


def scheme_color(value):
    if isinstance(value, libcarna.base.Color):
        return value.toarray()
    elif hasattr(value, '__len__') and len(value) == 4:
        return value
    else:
        raise ValueError(f'Found "{value}", expected color with 4 components (RGBA).')


shader_schemes = {
    'unshaded': {
        'color': scheme_color,
    },
    'solid': {
        'color': scheme_color,
    },
}


def material(shader_name: str = 'solid', **kwargs) -> libcarna.base.Material:
    """
    Create a :class:`libcarna.base.Material` object.

    Arguments:
        shader_name: The shader to be used for rendering.
        **kwargs: Uniform shader parameters.
    """
    assert shader_name in shader_schemes, (
        f'Unknown shader name: "{shader_name}" (supported: {", ".join(shader_schemes.keys())})'
    )
    shader_scheme = shader_schemes[shader_name]
    
    class Material(libcarna.base.Material):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            assert key in shader_scheme, (
                f'Unknown shader parameter: "{key}" (supported: {", ".join(shader_scheme.keys())})'
            )
            value = shader_scheme[key](value)
            super().__setitem__(key, value)

    material = Material(shader_name)
    for key, value in kwargs.items():
        material[key] = value
    return material
