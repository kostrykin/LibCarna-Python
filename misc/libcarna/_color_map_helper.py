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

    def __init__(
            self,
            color_map: libcarna.base.ColorMap,
            cmap: str | libcarna.base.ColorMap | None = None,
            clim: tuple[float | None, float | None] | None = None,
            default_n_samples: int = 50,
        ):
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
        if isinstance(cmap, libcarna.base.ColorMap):
            self.color_map.set(cmap)
        elif cmap in self.cmap_choices:
            getattr(self, cmap)()
        else:
            raise ValueError(f'Unknown color map: "{cmap}" (available: {", ".join(self.cmap_choices)})')
        
        # Set the color limits
        if clim is not None:
            self.limits(*clim)
        
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

    def write_linear_spline(self, *colors, ramp: float = 0.0, rampdegree: int = 1):
        """
        Write a linear spline to the color map. The colors are interpolated between the given colors.

        Arguments:
            colors: The colors to interpolate between.
            ramp: If `ramp > 0`, the alpha values of the colors are weighted by a ramp function, that starts with 0 and
                ends with 1. The `ramp` value is between 0 and 1, governing where the ramp function reaches 1.0.
            rampdegree: The degree of the ramp function. 1 is linear, 2 is quadratic, etc.
        """
        colors = list(colors)
        if ramp > 0:
            ramp_slope = 1 / ramp
            ramp_func = lambda t: min((1, pow(t * ramp_slope, rampdegree)))
            colors = [
                libcarna.color(color.r, color.g, color.b, round(color.a * ramp_func(t)))
                for color, t in zip(colors, np.linspace(0, 1, len(colors)))
            ]
        self.color_map.write_linear_spline(colors)

    def limits(self, *args) -> tuple[float | None, float | None] | None:
        """
        Get or set the limits of the color map.
        """
        if len(args) == 0:
            return (self.color_map.minimum_intensity, self.color_map.maximum_intensity)
        elif len(args) == 2:
            cmin, cmax = args
            if cmin is not None:
                self.color_map.minimum_intensity = cmin
            if cmax is not None:
                self.color_map.maximum_intensity = cmax
        else:
            raise ValueError('limits() takes 0 or 2 arguments, but {} were given'.format(len(args)))
