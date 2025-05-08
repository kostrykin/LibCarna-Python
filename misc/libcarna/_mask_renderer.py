import libcarna


class mask_renderer(libcarna.presets.MaskRenderingStage):
    """
    Renders 3D masks as either unshaded areas or borders.

    Arguments:
        geometry_type: Geometry type to be rendered.
        mask_role: Mask role to be used.
        color: Color to use for the mask.
        fill: If `True`, the mask is filled. If `False`, only the borders are rendered.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. MaskRenderingStage: example-setup-start
            :end-before: # .. MaskRenderingStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MaskRenderingStage.test__animated.png
            :width: 400
    """

    def __init__(
            self,
            geometry_type: int,
            mask_role: int = libcarna.presets.MaskRenderingStage.DEFAULT_ROLE_MASK,
            *,
            color: libcarna.color = libcarna.presets.MaskRenderingStage.DEFAULT_COLOR,
            fill: bool = False,
        ):
        super().__init__(geometry_type, mask_role)
        self.color = color
        self.filling = fill

    def replicate(self):
        """
        Replicate the mask renderer.
        """
        return mask_renderer(
            self.geometry_type,
            self.mask_role,
            color=self.color,
            fill=self.filling,
        )
