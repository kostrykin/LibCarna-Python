import numpy as np

import libcarna
from . import testsuite


class drr(testsuite.LibCarnaTestCase):

    def test__nuclei(self):
        img = libcarna.data.nuclei()
        self.assertEqual(img.shape, (60, 256, 256))
        self.assertEqual(img.dtype, np.uint16)

    def test__cthead(self):
        img = libcarna.data.cthead()
        self.assertEqual(img.shape, (256, 256, 99))
        self.assertEqual(img.dtype, np.uint16)

    def test__toy(self):
        img = libcarna.data.toy()
        self.assertEqual(img.shape, (64, 64, 20))
        self.assertEqual(img.dtype, np.float64)
        self.assertEqual(np.min(img), 0.0)
        self.assertEqual(np.max(img), 1.0)
