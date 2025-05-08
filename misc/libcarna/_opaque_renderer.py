import libcarna


class opaque_renderer(libcarna.presets.OpaqueRenderingStage):
    """
    Renders opaque geometries (meshes).

    Arguments:
        geometry_type: Geometry type to be rendered.

    Example:

        .. literalinclude:: ../test/test_integration.py
            :start-after: # .. OpaqueRenderingStage: example-setup-start
            :end-before: # .. OpaqueRenderingStage: example-setup-end
            :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test__animated.png
            :width: 400
    """

    def __init__(self, geometry_type: int):
        super().__init__(geometry_type)

    def replicate(self):
        """
        Replicate the opaque renderer.
        """
        return opaque_renderer(self.geometry_type)
