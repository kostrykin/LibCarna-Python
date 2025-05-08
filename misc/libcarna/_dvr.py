import libcarna

from ._color_map_helper import color_map_helper


class dvr(libcarna.presets.DVRStage):
    """
    Performs *Direct Volume Rendering* (DVR) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        cmap: Color map to use for the DVR. If `None`, the default color map is used.
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.
        transl: Translucency value for the DVR, that is used on top of the translucency from the color map. A value of
            1 means that the overall translucency is doubled. Larger values result in more translucency.
        diffuse: Diffuse light value for the volume rendering. Larger values result in more diffuse light. Ambient
            light is one minus diffuse light.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. DVRStage: example-setup-start
            :end-before: # .. DVRStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DVRStage.test__animated.png
            :width: 400
    """

    def __init__(
            self,
            geometry_type: int,
            *,
            cmap: str | libcarna.base.ColorMap | None = None,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            transl: float = libcarna.presets.DVRStage.DEFAULT_TRANSLUCENCY,
            diffuse: float = libcarna.presets.DVRStage.DEFAULT_DIFFUSE_LIGHT,
        ):
        super().__init__(geometry_type)
        self.cmap = color_map_helper(self.color_map, cmap)
        self.sample_rate = sr
        self.translucency = transl
        self.diffuse_light = diffuse

    def replicate(self):
        """
        Replicate the DVR.
        """
        return dvr(
            self.geometry_type,
            cmap=self.cmap.color_map,
            sr=self.sample_rate,
            transl=self.translucency,
            diffuse=self.diffuse_light,
        )
