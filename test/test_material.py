import libcarna

from . import testsuite


class material(testsuite.LibCarnaTestCase):

    def test__color__int(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(ValueError):
                    libcarna.material('unshaded', color=4)

    def test__color__str(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(TypeError):
                    libcarna.material('unshaded', color='teal')

    def test__color__3d(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(ValueError):
                    libcarna.material('unshaded', color=(1, 0, 0))
