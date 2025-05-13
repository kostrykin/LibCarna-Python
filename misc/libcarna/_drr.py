import libcarna
from ._alias import kwalias


class drr(libcarna.presets.DRRStage):
    """
    Renders *Digitally Reconstructed Radiographs* (DRR) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        sample_rate: Sample rate for volume rendering (alias: `sr`). Larger values result in higher quality and less
            artifacts, but slower rendering.
        water_attenuation: Water attenuation (alias: `waterat`).
        base_intensity: Base intensity (alias: `baseint`).
        lower_threshold: Lower threshold in Hounsfield Units (alias: `lothres`).
        upper_threshold: Upper threshold in Hounsfield Units (alias: `upthres`).
        upper_multiplier: Upper multiplier (alias: `upmulti`).
        render_inverse: If `True`, the image is rendered as gray-white on black background (alias: `inverse`).
            Otherwise, the image is rendered as gray-black on white background.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. DRRStage: example-setup-start
            :end-before: # .. DRRStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DRRStage.test__animated.png
            :width: 400
    """

    @kwalias('sample_rate', 'sr')
    @kwalias('water_attenuation', 'waterat')
    @kwalias('base_intensity', 'baseint')
    @kwalias('lower_threshold', 'lothres')
    @kwalias('upper_threshold', 'upthres')
    @kwalias('upper_multiplier', 'upmulti')
    @kwalias('render_inverse', 'inverse')
    def __init__(
            self,
            geometry_type: int,
            *,
            sample_rate: int         = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            water_attenuation: float = libcarna.presets.DRRStage.DEFAULT_WATER_ATTENUATION,
            base_intensity: float    = libcarna.presets.DRRStage.DEFAULT_BASE_INTENSITY,
            lower_threshold: int     = libcarna.presets.DRRStage.DEFAULT_LOWER_THRESHOLD,
            upper_threshold: int     = libcarna.presets.DRRStage.DEFAULT_UPPER_THRESHOLD,
            upper_multiplier: float  = libcarna.presets.DRRStage.DEFAULT_UPPER_MULTIPLIER,
            render_inverse: bool     = libcarna.presets.DRRStage.DEFAULT_RENDER_INVERSE,
        ):
        super().__init__(geometry_type)
        self.sample_rate = sample_rate
        self.water_attenuation = water_attenuation
        self.base_intensity    = base_intensity
        self.lower_threshold   = lower_threshold
        self.upper_threshold   = upper_threshold
        self.upper_multiplier  = upper_multiplier
        self.render_inverse    = render_inverse

    def replicate(self):
        """
        Replicate the DRR renderer.
        """
        return drr(
            self.geometry_type,
            sample_rate=self.sample_rate,
            water_attenuation=self.water_attenuation,
            base_intensity=self.base_intensity,
            lower_threshold=self.lower_threshold,
            upper_threshold=self.upper_threshold,
            upper_multiplier=self.upper_multiplier,
            render_inverse=self.render_inverse,
        )
