import libcarna

from ._color_map_helper import color_map_helper


class mip(libcarna.presets.MIPStage):
    """
    Renders *Maximum Intensity Projections* (MIP) of volume geometries.

    Arguments:
        geometry_type: Geometry type to be rendered.
        cmap: Color map to use for the MIP. If `None`, the default color map is used.
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
            sr: int = libcarna.presets.VolumeRenderingStage.DEFAULT_SAMPLE_RATE,
        ):
        super().__init__(geometry_type)
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
