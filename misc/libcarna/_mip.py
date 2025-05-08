import libcarna

from ._colormap_helper import colormap_helper


class mip(libcarna.presets.MIPStage):
    """
    Renders *Maximum Intensity Projections* (MIP) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        cmap: Color map to use for the MIP. If `None`, the default color map is used.
        clim: Color limits for the color map. If `None`, the full range of intensities [0, 1] is used (if `cmap` is
            `str` or `None`) or the limits of `cmap` are used (if `cmap` is a :class:`libcarna.base.ColorMap` ).
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. MIPStage: example-setup-start
            :end-before: # .. MIPStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MIPStage.test__animated.png
            :width: 400
    """

    def __init__(
            self,
            geometry_type: int,
            *,
            cmap: str | None = None,
            clim: tuple[float | None, float | None] | None = None,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
        ):
        super().__init__(geometry_type)
        self.cmap = colormap_helper(self.color_map, cmap, clim)
        self.sample_rate = sr

    def replicate(self):
        """
        Replicate the MIP stage.
        """
        return mip(
            self.geometry_type,
            cmap=self.cmap.colormap,
            sr=self.sample_rate,
            clim=None,  # uses the color limits from `cmap`
        )
