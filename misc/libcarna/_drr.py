import libcarna


class drr(libcarna.presets.DRRStage):
    """
    DRR (digitally reconstructed radiograph).

    Arguments:
        *args: Passed to :class:`libcarna.presets.DRRStage`.
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.
        waterat: Water attenuation.
        baseint: Base intensity.
        lothres: Lower threshold.
        upthres: Upper threshold.
        upmulti: Upper multiplier.
        inverse: Inverse rendering (white on black background).
        **kwargs: Passed to :class:`libcarna.presets.DRRStage`.
    """

    def __init__(
            self,
            *args,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            waterat: float = libcarna.presets.DRRStage.DEFAULT_WATER_ATTENUATION,
            baseint: float = libcarna.presets.DRRStage.DEFAULT_BASE_INTENSITY,
            lothres: float = libcarna.presets.DRRStage.DEFAULT_LOWER_THRESHOLD,
            upthres: float = libcarna.presets.DRRStage.DEFAULT_UPPER_THRESHOLD,
            upmulti: float = libcarna.presets.DRRStage.DEFAULT_UPPER_MULTIPLIER,
            inverse: bool  = libcarna.presets.DRRStage.DEFAULT_RENDER_INVERSE,
            **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.sample_rate = sr
        self.water_attenuation = waterat
        self.base_intensity    = baseint
        self.lower_threshold   = lothres
        self.upper_threshold   = upthres
        self.upper_multiplier  = upmulti
        self.render_inverse    = inverse

    def replicate(self):
        """
        Replicate the DRR stage.
        """
        return drr(
            self.geometry_type,
            sr=self.sample_rate,
            waterat=self.water_attenuation,
            baseint=self.base_intensity,
            lothres=self.lower_threshold,
            upthres=self.upper_threshold,
            upmulti=self.upper_multiplier,
            inverse=self.render_inverse,
        )
