import glob
import tarfile
import tempfile

import numpy as np
import pooch
import skimage.data
import tifffile

import libcarna


def nuclei():
    """
    Returns a sample image of cell nuclei.

    The image is from the Allen Cell WTC-11 hiPSC Single-Cell Image Dataset: https://doi.org/10.1038/s41586-022-05563-7
    (Viana et al. 2023).

    The data is 60 × 256 × 256 pixels (uint16). The spacings should have a ratio of 2:1:1.
    """
    return skimage.data.cells3d()[:, 1]


def cthead(normalize: bool = False) -> np.ndarray:
    """
    Returns a computer tomography (CT) study of a cadaver head: https://graphics.stanford.edu/data/voldata/

    The data is 256 × 256 × 99 pixels (uint16). The image intensities are *not* normalized to Hounsfield Units. The
    spacings should have a ratio of 1:1:2.

    Arguments:
        normalize: If True, the image intensities are heuristically normalized to Hounsfield Units (HU).
    """
    data_tar_gz_filepath = pooch.retrieve(
        'https://graphics.stanford.edu/data/voldata/cthead-16bit.tar.gz',
        known_hash='md5:ea5874800bc1321fecd65ee791ca157b',
    )
    with tempfile.TemporaryDirectory() as data_dir_path:
        with tarfile.open(data_tar_gz_filepath) as data_tar_gz:
            kwargs = dict()
            if hasattr(tarfile, 'fully_trusted_filter'):
                kwargs['filter'] = tarfile.fully_trusted_filter  # required by tarfile >= 3.7.0
            data_tar_gz.extractall(data_dir_path, **kwargs)
        data = np.dstack(
            [
                tifffile.imread(filepath) for filepath in
                sorted(glob.glob(f'{data_dir_path}/cthead-*.tif'))
            ]
        )
        if normalize:
            data = libcarna.normalize_hounsfield_units(data)
        return data