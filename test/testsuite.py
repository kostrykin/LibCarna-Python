import glob
import io
import pathlib
import re
import unittest

import faulthandler
faulthandler.enable()

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
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

    @staticmethod
    def _get_expected_image_filepath(filename: str, vendor: str | None) -> str:
        results_path = pathlib.Path('test/results')
        if vendor is None:
            return str(results_path / 'expected' / filename)
        else:
            for filepath in glob.glob(str(results_path / 'expected_*' / filename)):
                m = re.match(r'^.*/expected_(.*)/.*$', filepath)
                if m is not None and m.group(1).lower() in re.split(r'[^a-zA-Z0-9]', vendor.lower()):
                    return filepath
            return LibCarnaRenderingTestCase._get_expected_image_filepath(filename, vendor=None)

    def assert_image_almost_equal(
            self,
            actual: np.ndarray,
            expected: str | np.ndarray,
            blur: float = 1,
            threshold: float = 1,
            max_differing_pixels: int = 0,
            vendor: str | None = None,
        ):
        """
        Compare two images, `actual` and `expected`, and assert that they are almost equal.

        The comparison is done by, first, blurring out small details in the images, and then counting the number of
        pixels for which the channel-wise difference exceeds a certain` threshold`. The test fails if the number of
        differing pixels exceeds `max_differing_pixels`.

        The comparison is performed individually for each frame of an image sequence.
        """
        assert not np.issubdtype(actual.dtype, np.floating)

        # If `expected` is a string, read the image from the path.
        if isinstance(expected, str):
            print('***', LibCarnaRenderingTestCase._get_expected_image_filepath(expected, vendor=vendor))
            expected = _imread(LibCarnaRenderingTestCase._get_expected_image_filepath(expected, vendor=vendor))

            # If the image is in floating point format, convert it to [0, 255] range.
            if np.issubdtype(expected.dtype, np.floating):
                expected = (expected * 255)

        # Define routine for pairwise comparison of `actual` and `expected` frames.
        def verify_frame(actual, expected):
            if blur > 0:
                actual = ndi.gaussian_filter(actual.astype(float), sigma=blur, axes=(0, 1))
                expected = ndi.gaussian_filter(expected.astype(float), sigma=blur, axes=(0, 1))
            self.assertLessEqual((np.max(np.abs(actual - expected), axis=2) > threshold).sum(), max_differing_pixels)

        # If the image is a single frame, compare it directly.
        self.assertEqual(actual.shape, expected.shape)
        if actual.ndim == 3:
            verify_frame(actual, expected)

        # If the image is a multi-frame image sequence, compare each frame of the sequence.
        elif actual.ndim == 4:
            for actual_frame, expected_frame in zip(actual, expected):
                verify_frame(actual_frame, expected_frame)

        # Complain that we don't know how to handle the shape of the image.
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