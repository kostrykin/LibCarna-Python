import numpy as np
import scipy.ndimage as ndi


def normalize_hounsfield_units(data, rel_mode_width=.33):
    """
    Normalize `data` to Hounsfield Units (HU) using a heuristic histogram method.
    """
    assert 0 < rel_mode_width <= 1, f'Unsupported rel_mode_width: {rel_mode_width}'
    data = data - data.min()
    h = np.bincount(data.reshape(-1))
    h_peaks_mask = (ndi.maximum_filter(h, size=len(h) / 3) == h)
    if h_peaks_mask[-1] and h_peaks_mask.sum() == 4:
        h_peaks_mask[-1] = False
    h_modes = h_peaks_mask.sum()
    assert h_modes == 3, f'Heuristic normalization failed: Histogram has {h_modes} mode(s), but 3 required.'
    i_air, i_bone = np.where(h_peaks_mask)[0][np.array((0, -1))]
    return (2000 * (data.astype(int) - i_air) / (i_bone - i_air) - 1024).round().clip(-1024, +3071).astype(np.int16)
