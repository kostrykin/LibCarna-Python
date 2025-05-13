import io
import pathlib
import unittest

import faulthandler
faulthandler.enable()

import matplotlib.pyplot as plt
import numpy as np
from apng import APNG
from numpngw import write_apng
from PIL import Image


def _imread(path: str) -> np.ndarray:
    """
    Reads a PNG as a `YXC` array, and APNG as a `TYXC` array.
    """

    def read_png_frame(buf) -> np.ndarray:
        with Image.open(io.BytesIO(buf)) as im:
            array = np.array(im)
            array = array[:, :, :3]  # Ignore alpha channel if present
            return array

    im = APNG.open(path)
    array = np.array(
        [
            read_png_frame(frame[0].to_bytes())
            for frame in im.frames
        ]
    )

    # Convert `TYXC` to `YXC` format (APNG -> PNG)
    if array.shape[0] == 1 and array.ndim == 4:
        array = array[0]

    return array


def _imsave(path: str, array: np.ndarray):
    if array.ndim == 4:

        # Palette APNG cannot be read proplery by the apng library
        write_apng(path, array, delay=40, use_palette=False)

    else:
        plt.imsave(path, array)


class LibCarnaTestCase(unittest.TestCase):

    pass


class LibCarnaRenderingTestCase(LibCarnaTestCase):

    def assert_image_almost_equal(self, actual, expected, threshold=1, max_differing_pixels=0):
        if isinstance(actual, str):
            actual = _imread(actual)
        if isinstance(expected, str):
            expected = pathlib.Path('test/results/expected') / expected
            expected = _imread(str(expected))
            if np.issubdtype(expected.dtype, np.floating):
                expected = (expected * 255).astype(np.uint8)

        def verify_frame(actual, expected):
            self.assertLessEqual((np.max(np.abs(actual - expected), axis=2) > threshold).sum(), max_differing_pixels)

        self.assertEqual(actual.shape, expected.shape)
        if actual.ndim == 3:
            verify_frame(actual, expected)

        elif actual.ndim == 4:
            for actual_frame, expected_frame in zip(actual, expected):
                verify_frame(actual_frame, expected_frame)

        else:
            raise ValueError(f'Unsupported array shape: {actual.shape}')

    def assert_image_almost_expected(self, actual, **kwargs):
        expected = f'{self.id()}.png'
        try:
            self.assert_image_almost_equal(actual, expected, **kwargs)
        except:
            actual_path = pathlib.Path('test/results/actual') / f'{expected}'
            actual_path.parent.mkdir(parents=True, exist_ok=True)
            _imsave(actual_path, actual)
            print(f'Test result was written to: {actual_path.resolve()}')
            raise