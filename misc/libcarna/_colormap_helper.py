from typing import Iterable

import matplotlib as mpl
import numpy as np

import libcarna
from ._colorbar import colorbar


def _sample_colormap(mpl_cmap: mpl.colors.Colormap, n_samples: int) -> list[libcarna.color]:
    """
    Sample a colormap from matplotlib and return the list of colors.
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


class colormap_helper:

    def __init__(
            self,
            colormap: libcarna.base.ColorMap,
            cmap: str | libcarna.base.ColorMap | None = None,
            clim: tuple[float | None, float | None] | None = None,
        ):
        self.colormap = colormap
        self.cmap_choices = list()
        cmap = cmap or 'viridis'

        # Import colormaps
        for cmap_name, _ in _mpl_colormaps():
            self.cmap_choices.append(cmap_name)

        # Set the requested colormap
        if isinstance(cmap, libcarna.base.ColorMap):
            self.colormap.set(cmap)
        elif isinstance(cmap, str) and cmap in self.cmap_choices:
            self(cmap)
        else:
            raise ValueError(f'Unknown color map: "{cmap}" (available: {", ".join(self.cmap_choices)})')
        
        # Set the color limits
        if clim is not None:
            self.limits(*clim)

    def __call__(self, cmap_name: str, n_samples: int = 50, **kwargs):
        if cmap_name in self.cmap_choices:
            mpl_cmap = mpl.colormaps[cmap_name]
            n_samples = n_samples or self.default_n_samples
            colors = _sample_colormap(mpl_cmap, n_samples)
            self.linear_spline(*colors, **kwargs)
        else:
            raise ValueError(f'Unknown color map: "{cmap_name}" (available: {", ".join(self.cmap_choices)})')
        
    def clear(self):
        """
        Clear the color map.
        """
        self.colormap.clear()
        
    def linear_segment(
            self,
            intensity_first: float,
            intensity_last: float,
            color_first: libcarna.base.Color,
            color_last: libcarna.base.Color,
        ):
        """
        Write a linear segment to the color map.
        """
        self.colormap.write_linear_segment(
            intensity_first,
            intensity_last,
            color_first,
            color_last,
        )

    def linear_spline(self, *colors, ramp: tuple[float, float] | None = None, rampdegree: int = 1):
        """
        Write a linear spline to the color map. The colors are interpolated between the given colors.

        Arguments:
            colors: The colors to interpolate between.
            ramp: If `ramp` is not `None`, the alpha values of the colors are weighted by a ramp function, that starts
                with 0 at `ramp[0]` and ends with 1 at `ramp[1]`.
            rampdegree: The degree of the ramp function. 1 is linear, 2 is quadratic, etc.
        """
        colors = list(colors)
        if ramp is not None:
            ramp_width = max(ramp) - min(ramp)
            ramp_func = lambda t: np.clip((t - min(ramp)) / ramp_width, 0, 1) ** rampdegree
            colors = [
                libcarna.color(color.r, color.g, color.b, round(color.a * ramp_func(t)))
                for color, t in zip(colors, np.linspace(0, 1, len(colors)))
            ]
        self.colormap.write_linear_spline(colors)

    def limits(self, *args) -> tuple[float | None, float | None] | None:
        """
        Get or set the limits of the color map.
        """
        if len(args) == 0:
            return (self.colormap.minimum_intensity, self.colormap.maximum_intensity)
        elif len(args) == 2:
            cmin, cmax = args
            if cmin is not None:
                self.colormap.minimum_intensity = cmin
            if cmax is not None:
                self.colormap.maximum_intensity = cmax
        else:
            raise ValueError('limits() takes 0 or 2 arguments, but {} were given'.format(len(args)))
        
    def bar(self, volume: libcarna.base.Node, **kwargs) -> colorbar:
        """
        Return a colorbar object for the colormap.
        """
        normalized_intensity_limits = self.limits()
        raw_intensity_limits = volume.raw(normalized_intensity_limits)
        colorlist = self.colormap.color_list
        return colorbar(colorlist, *raw_intensity_limits, **kwargs)
