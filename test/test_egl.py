import carna.egl

import testsuite


class Context(testsuite.CarnaTestCase):

    def test__attach_child(self):
        ctx = carna.egl.Context()
        del ctx