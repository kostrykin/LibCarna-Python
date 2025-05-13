import libcarna
from ._alias import kwalias
from ._colormap_helper import colormap_helper


class dvr(libcarna.presets.DVRStage):
    """
    Performs *Direct Volume Rendering* (DVR) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        cmap: Color map to use for the DVR. If `None`, the default color map is used.
        clim: Color limits for the color map. If `None`, the full range of intensities [0, 1] is used (if `cmap` is
            `str` or `None`) or the limits of `cmap` are used (if `cmap` is a :class:`libcarna.base.ColorMap` ).
        sample_rate: Sample rate for volume rendering (alias: `sr`). Larger values result in higher quality and less
            artifacts, but slower rendering.
        translucency: Translucency value for the DVR, that is used on top of the translucency from the color map
            (alias: `transl`). A value of 1 means that the overall translucency is doubled. Larger values result in
            more translucency.
        diffuse_light: Diffuse light value for the volume rendering. Larger values result in more diffuse light
            (alias: `diffuse`). Ambient light is one minus diffuse light.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. DVRStage: example-setup-start
            :end-before: # .. DVRStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DVRStage.test__animated.png
            :width: 400
    """

    @kwalias('sample_rate', 'sr')
    @kwalias('translucency', 'transl')
    @kwalias('diffuse_light', 'diffuse')
    def __init__(
            self,
            geometry_type: int,
            *,
            cmap: str | libcarna.base.ColorMap | None = None,
            clim: tuple[float | None, float | None] | None = None,
            sample_rate: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            translucency: float = 0,
            diffuse_light: float = libcarna.presets.DVRStage.DEFAULT_DIFFUSE_LIGHT,
        ):
        super().__init__(geometry_type)
        self.cmap = colormap_helper(self.color_map, cmap, clim)
        self.sample_rate = sample_rate
        self.translucency = translucency
        self.diffuse_light = diffuse_light

    def replicate(self):
        """
        Replicate the DVR.
        """
        return dvr(
            self.geometry_type,
            cmap=self.cmap.colormap,
            clim=None,  # uses the color limits from `cmap`
            sample_rate=self.sample_rate,
            translucency=self.translucency,
            diffuse_light=self.diffuse_light,
        )
