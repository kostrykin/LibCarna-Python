import gc
import pathlib
import os
import unittest

import faulthandler
faulthandler.enable()

import matplotlib.pyplot as plt
import numpy as np


class CarnaTestCase(unittest.TestCase):

    pass


class CarnaRenderingTestCase(CarnaTestCase):

    def assert_image_almost_equal(self, actual, expected, decimal=5):
        if isinstance(actual, str):
            actual = plt.imread(actual)
        if isinstance(expected, str):
            expected = pathlib.Path('test/results/expected') / expected
            expected = plt.imread(str(expected))
            expected = expected[:, :, :3]  # Ignore alpha channel if present
            if np.issubdtype(expected.dtype, np.floating):
                expected = (expected * 255).astype(np.uint8)
        np.testing.assert_array_almost_equal(actual, expected, decimal=decimal)

    def assert_image_almost_expected(self, actual, **kwargs):
        expected = f'{self.id()}.png'
        try:
            self.assert_image_almost_equal(actual, expected, **kwargs)
        except:
            actual_path = pathlib.Path('test/results/actual') / f'{expected}'
            actual_path.parent.mkdir(parents=True, exist_ok=True)
            plt.imsave(actual_path, actual)
            print(f'Test result was written to: {actual_path.resolve()}')
            raise