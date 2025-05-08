import libcarna

from ._colormap_helper import colormap_helper


class cutting_planes(libcarna.presets.CuttingPlanesStage):
    """
    Renders cutting planes (cross sections) of volume geometries.

    Arguments:
        volume_geometry_type: Geometry type of volumes to be rendered.
        plane_geometry_type: Geometry type of planes to be rendered.
        cmap: Color map to use for the rendering. If `None`, the default color map is used.
        clim: Color limits for the color map. If `None`, the full range of intensities [0, 1] is used (if `cmap` is
            `str` or `None`) or the limits of `cmap` are used (if `cmap` is a :class:`libcarna.base.ColorMap` ).

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
            cmap: str | libcarna.base.ColorMap | None = None,
            clim: tuple[float | None, float | None] | None = None,
        ):
        super().__init__(volume_geometry_type, plane_geometry_type)
        self.cmap = colormap_helper(self.color_map, cmap, clim)

    def replicate(self):
        """
        Replicate the cutting planes renderer.
        """
        return cutting_planes(
            self.volume_geometry_type,
            self.plane_geometry_type,
            cmap=self.cmap.colormap,
            clim=None,  # uses the color limits from `cmap`
        )
