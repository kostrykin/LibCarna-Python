import libcarna

from ._color_map_helper import color_map_helper


class mip(libcarna.presets.MIPStage):
    """
    MIP (Maximum Intensity Projection).

    Arguments:
        *args: Passed to :class:`libcarna.presets.MIPStage`.
        cmap: Color map to use for the MIP. If `None`, the default color map is used.
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.
        **kwargs: Passed to :class:`libcarna.presets.MIPStage`.
    """

    def __init__(
            self,
            *args,
            cmap: str | None = None,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.cmap = color_map_helper(self.color_map, cmap)
        self.sample_rate = sr

    def replicate(self):
        """
        Replicate the MIP stage.
        """
        return mip(
            self.geometry_type,
            cmap=self.cmap.color_map,
            sr=self.sample_rate,
        )
