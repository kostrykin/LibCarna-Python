import libcarna


class drr(libcarna.presets.DRRStage):
    """
    Renders *Digitally Reconstructed Radiographs* (DRR) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        sr: Sample rate for volume rendering. Larger values result in higher quality and less artifacts, but slower
            rendering.
        waterat: Water attenuation.
        baseint: Base intensity.
        lothres: Lower threshold (in Hounsfield Units).
        upthres: Upper threshold (in Hounsfield Units).
        upmulti: Upper multiplier.
        inverse: Inverse rendering (white on black background).

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. DRRStage: example-setup-start
            :end-before: # .. DRRStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DRRStage.test__animated.png
            :width: 400
    """

    def __init__(
            self,
            geometry_type: int,
            *,
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            waterat: float = libcarna.presets.DRRStage.DEFAULT_WATER_ATTENUATION,
            baseint: float = libcarna.presets.DRRStage.DEFAULT_BASE_INTENSITY,
            lothres: int   = libcarna.presets.DRRStage.DEFAULT_LOWER_THRESHOLD,
            upthres: int   = libcarna.presets.DRRStage.DEFAULT_UPPER_THRESHOLD,
            upmulti: float = libcarna.presets.DRRStage.DEFAULT_UPPER_MULTIPLIER,
            inverse: bool  = libcarna.presets.DRRStage.DEFAULT_RENDER_INVERSE,
        ):
        super().__init__(geometry_type)
        self.sample_rate = sr
        self.water_attenuation = waterat
        self.base_intensity    = baseint
        self.lower_threshold   = lothres
        self.upper_threshold   = upthres
        self.upper_multiplier  = upmulti
        self.render_inverse    = inverse

    def replicate(self):
        """
        Replicate the DRR renderer.
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
