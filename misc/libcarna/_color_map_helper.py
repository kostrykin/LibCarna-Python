from typing import Literal

import libcarna


class color_map_helper:

    def __init__(self, color_map: libcarna.base.ColorMap, cmap: str | None = None):
        self.color_map = color_map
        cmap = cmap or 'viridis'
        if hasattr(self, cmap) and cmap != 'write_colors':
            getattr(self, cmap)()
        else:
            raise ValueError(f'Unknown color map: "{cmap}"')

    def write_colors(self, *colors, start: Literal['opaque', 'make-transparent', 'add-transparent'] = 'opaque'):
        colors = list(colors)
        if start == 'make-transparent':
            colors[0] += '00'
        elif start == 'add-transparent':
            colors.insert(0, colors[0] + '00')
        self.color_map.write_linear_spline(colors)

    def gray(self, **kwargs):
        self.write_colors(
            libcarna.color('#000000'),
            libcarna.color('#ffffff'),
            **kwargs,
        )

    def viridis(self, **kwargs):
        self.write_colors(
            libcarna.color('#440154'),
            libcarna.color('#482777'),
            libcarna.color('#3e4989'),
            libcarna.color('#31688e'),
            libcarna.color('#26828e'),
            libcarna.color('#1f9e89'),
            libcarna.color('#35b779'),
            libcarna.color('#6ece58'),
            libcarna.color('#b5de2b'),
            libcarna.color('#fde725'),
            **kwargs,
        )

    def jet(self, **kwargs):
        self.write_colors(
            libcarna.color('#00007f'),
            libcarna.color('#0000ff'),
            libcarna.color('#007fff'),
            libcarna.color('#00ffff'),
            libcarna.color('#7fff7f'),
            libcarna.color('#ffff00'),
            libcarna.color('#ff7f00'),
            libcarna.color('#ff0000'),
            libcarna.color('#7f0000'),
            **kwargs,
        )
