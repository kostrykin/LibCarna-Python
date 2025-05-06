from typing import Iterable

import matplotlib as mpl
import numpy as np

import libcarna


def _sample_color_map(mpl_cmap: mpl.colors.Colormap, n_samples: int) -> list[libcarna.color]:
    """
    Sample a color map from matplotlib and return the list of colors.
    """
    return [libcarna.color(mpl_cmap(i)) for i in np.linspace(0, 1, n_samples)]


def _mpl_colormaps() -> Iterable[str]:
    """
    Get all non-discrete colormaps from matplotlib. Yield pairs of the name and the corresponding colormap.
    """
    for cmap_name in mpl.colormaps():
        mpl_cmap = mpl.colormaps[cmap_name]
        if isinstance(mpl_cmap, mpl.colors.LinearSegmentedColormap) or (
            isinstance(mpl_cmap, mpl.colors.ListedColormap) and mpl_cmap.N >= 256
        ):
            yield cmap_name, mpl_cmap


class color_map_helper:

    def __init__(self, color_map: libcarna.base.ColorMap, cmap: str | None = None, default_n_samples: int = 50):
        self.color_map = color_map
        self.cmap_choices = list()
        cmap = cmap or 'viridis'

        # Import colormaps
        def create_cmap_func(mpl_cmap: mpl.colors.Colormap):
            def cmap_func(**kwargs):
                n_samples = kwargs.pop('n_samples', default_n_samples)
                colors = _sample_color_map(mpl_cmap, n_samples)
                self.write_linear_spline(*colors, **kwargs)
            return cmap_func
        for cmap_name, mpl_cmap in _mpl_colormaps():
            cmap_func = create_cmap_func(mpl_cmap)
            setattr(self, cmap_name, cmap_func)
            self.cmap_choices.append(cmap_name)

        # Set the requested colormap
        if cmap in self.cmap_choices:
            getattr(self, cmap)()
        else:
            raise ValueError(f'Unknown color map: "{cmap}" (available: {", ".join(self.cmap_choices)})')
        
    def clear(self):
        """
        Clear the color map.
        """
        self.color_map.clear()
        
    def write_linear_segment(
            self,
            intensity_first: float,
            intensity_last: float,
            color_first: libcarna.base.Color,
            color_last: libcarna.base.Color,
        ):
        """
        Write a linear segment to the color map.
        """
        self.color_map.write_linear_segment(
            intensity_first,
            intensity_last,
            color_first,
            color_last,
        )

    def write_linear_spline(self, *colors):
        """
        Write a linear spline to the color map. The colors are interpolated between the given colors.
        """
        colors = list(colors)
        self.color_map.write_linear_spline(colors)
