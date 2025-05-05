import libcarna


def material(shader_name: str, **kwargs) -> libcarna.base.Material:
    """
    Create a :class:`libcarna.base.Material` object.

    Arguments:
        shader_name: The shader to be used for rendering.
        **kwargs: Uniform shader parameters.
    """
    class Material(libcarna.base.Material):

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
