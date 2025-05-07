import libcarna


class cutting_planes(libcarna.presets.CuttingPlanesStage):
    """
    Renders cutting planes (cross sections) of volume geometries in the scene.

    Arguments:
        *args: Passed to :class:`libcarna.presets.CuttingPlanesStage`.
        windowing_level: The windowing level of the cutting planes. This is the center of the range of values that
            are displayed.
        windowing_width: The windowing width of the cutting planes. This is the range of values that are displayed.
        **kwargs: Passed to :class:`libcarna.presets.CuttingPlanesStage`.
    """

    def __init__(
            self,
            *args,
            windowing_level=libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_LEVEL,
            windowing_width=libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_WIDTH,
            **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.windowing_level = windowing_level
        self.windowing_width = windowing_width

    def replicate(self):
        """
        Replicate the cutting planes stage.
        """
        return cutting_planes(
            self.volume_geometry_type,
            self.plane_geometry_type,
            windowing_level=self.windowing_level,
            windowing_width=self.windowing_width,
        )
