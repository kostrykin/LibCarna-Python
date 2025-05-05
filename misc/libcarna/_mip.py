import libcarna

from ._color_map_helper import color_map_helper


class mip(libcarna.presets.MIPStage):

    def __init__(self, *args, cmap: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmap = color_map_helper(self.color_map, cmap)
