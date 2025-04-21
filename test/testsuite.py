import gc
import pathlib
import unittest

import faulthandler
faulthandler.enable()

import matplotlib.pyplot as plt
import numpy as np

import carna

extra_checks = hasattr(carna.base, 'debug_events')


class CarnaTestCase(unittest.TestCase):

    def setUp(self):
        if extra_checks:
            carna.base.debug_events()  # Clear events before the test starts

    def tearDown(self):
        if extra_checks:
            gc.collect()
            debug_events = carna.base.debug_events()
            memory_leaks, double_frees = analyze_debug_events(debug_events)
            self.assertEqual(memory_leaks, 0, f"Memory leaks detected: {memory_leaks}")
            self.assertEqual(double_frees, 0, f"Double frees detected: {double_frees}")


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


def analyze_debug_events(debug_events):
    allocations = set()
    double_frees = 0
    for event_str in debug_events:
        event = event_str.split(': ')
        match event[1]:
            case 'created':
                allocations.add(event[0])
            case 'deleted':
                if event[0] in allocations:
                    allocations.remove(event[0])
                else:
                    double_frees += 1
    memory_leaks = len(allocations)
    return memory_leaks, double_frees