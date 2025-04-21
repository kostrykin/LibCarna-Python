import carna

import testsuite


class material(testsuite.CarnaTestCase):

    def test__color__int(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(ValueError):
                    carna.material('unshaded', color=4)

    def test__color__str(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(TypeError):
                    carna.material('unshaded', color='teal')

    def test__color__3d(self):
        for shader_name in ('unshaded', 'solid'):
            with self.subTest(shader_name=shader_name):
                with self.assertRaises(ValueError):
                    carna.material('unshaded', color=(1, 0, 0))