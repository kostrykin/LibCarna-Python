import libcarna
from ._alias import kwalias


class mask_renderer(libcarna.presets.MaskRenderingStage):
    """
    Renders 3D masks as either unshaded areas or borders.

    Arguments:
        geometry_type: Geometry type to be rendered.
        sample_rate: Sample rate for volume rendering (alias: `sr`). Larger values result in higher quality and less
            artifacts, but slower rendering.
        color: Color to use for the mask (alias: `c`).
        filling: If `True`, the mask is filled (alias: `fill`). If `False`, only the borders are rendered.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. MaskRenderingStage: example-setup-start
            :end-before: # .. MaskRenderingStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MaskRenderingStage.test__animated.png
            :width: 400
    """

    @kwalias('sample_rate', 'sr')
    @kwalias('color', 'c')
    @kwalias('filling', 'fill')
    def __init__(
            self,
            geometry_type: int,
            *,
            sample_rate: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
            color: libcarna.color = libcarna.presets.MaskRenderingStage.DEFAULT_COLOR,
            filling: bool = False,
        ):
        super().__init__(geometry_type, mask_role=0)
        self.sample_rate = sample_rate
        self.color = color
        self.filling = filling

    def replicate(self):
        """
        Replicate the mask renderer.
        """
        return mask_renderer(
            self.geometry_type,
            sample_rate=self.sample_rate,
            color=self.color,
            filling=self.filling,
        )
