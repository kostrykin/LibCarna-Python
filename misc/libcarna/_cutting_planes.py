import libcarna


class cutting_planes(libcarna.presets.CuttingPlanesStage):
    """
    Renders cutting planes (cross sections) of volume geometries.

    Arguments:
        volume_geometry_type: Geometry type of volumes to be rendered.
        plane_geometry_type: Geometry type of planes to be rendered.
        windowing_level: The windowing level of the cutting planes. This is the center of the range of values that
            are displayed.
        windowing_width: The windowing width of the cutting planes. This is the range of values that are displayed.

    Example:

    .. literalinclude:: ../test/test_integration.py
        :start-after: # .. CuttingPlanesStage: example-setup-start
        :end-before: # .. CuttingPlanesStage: example-setup-end
        :dedent: 8

    The normal vector of the planes does not have to necessarily align with the axes.

    In this example, we have a z-plane and a pair of x-planes. The x-planes are positioned on the left and right
    faces of the volume. Their distances to the center of the volume calculates as the width of the volume divided
    by 2.

    For a more information-rich visualization of the volume, we will make the z-plane bounce between the front and
    back faces of the volume. The amplitude is calculated as the depth of the volume divided by 2.

    .. literalinclude:: ../test/test_integration.py
        :start-after: # .. CuttingPlanesStage: example-animation-start
        :end-before: # .. CuttingPlanesStage: example-animation-end
        :dedent: 8

    The example yields this animation:

    .. image:: ../test/results/expected/test_integration.CuttingPlanesStage.test__animated.png
        :width: 400
    """

    def __init__(
            self,
            volume_geometry_type: int,
            plane_geometry_type: int,
            *,
            windowing_level=libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_LEVEL,
            windowing_width=libcarna.presets.CuttingPlanesStage.DEFAULT_WINDOWING_WIDTH,
        ):
        super().__init__(volume_geometry_type, plane_geometry_type)
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
