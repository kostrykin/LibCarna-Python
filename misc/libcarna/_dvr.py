import libcarna

from ._color_map_helper import color_map_helper


class dvr(libcarna.presets.DVRStage):
    """
    DVR (direct volume rendering).

    Arguments:
        *args: Passed to :class:`libcarna.presets.DVRStage`.
        cmap: Color map to use for the DVR. If `None`, the default color map is used.
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.
        transl: Translucency value for the DVR, that is used on top of the translucency from the color map. A value of
            1 means that the overall translucency is doubled. Larger values result in more translucency.
        diffuse: Diffuse light value for the volume rendering. Larger values result in more diffuse light. Ambient
            light is one minus diffuse light.
        **kwargs: Passed to :class:`libcarna.presets.DVRStage`.
    """

    def __init__(
            self,
            *args,
            cmap: str | None = None,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            transl: float = libcarna.presets.DVRStage.DEFAULT_TRANSLUCENCY,
            diffuse: float = libcarna.presets.DVRStage.DEFAULT_DIFFUSE_LIGHT,
            **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.cmap = color_map_helper(self.color_map, cmap)
        self.sample_rate = sr
        self.translucency = transl
        self.diffuse_light = diffuse
