import libcarna


class color(libcarna.base.Color):

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], str) and args[0].startswith('#'):
            hex_str = args[0][1:]
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16) if len(hex_str) == 8 else 255
            super().__init__(r, g, b, a)
        else:
            super().__init__(*args, **kwargs)
