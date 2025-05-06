import numpy as np

import libcarna

from ._axes import AxisHint, resolve_axis_hint


class transform:

    def __init__(self, mat: np.ndarray):
        self.mat = mat
    
    def rotate(self, *args, **kwargs):
        return transform(rotate(*args, **kwargs).mat @ self.mat)
    
    def scale(self, *args, **kwargs):
        return transform(scale(*args, **kwargs).mat @ self.mat)
    
    def translate(self, *args, **kwargs):
        return transform(translate(*args, **kwargs).mat @ self.mat)
    
    def plane(self, *args, **kwargs):
        return transform(plane(*args, **kwargs).mat @ self.mat)
    
    def point(self, xyz: np.ndarray = np.zeros(3)) -> np.ndarray:
        return self.mat @ np.array([*xyz, 1.0])
    
    def intpoint(self, *args, **kwargs) -> tuple[int, int, int]:
        return tuple(self.point(*args, **kwargs).round().astype(int))[:3]
    
    def direction(self, xyz: np.ndarray = np.zeros(3)) -> np.ndarray:
        return self.mat @ np.array([*xyz, 0.0])


def rotate(axis: AxisHint, deg: float) -> transform:
    axis = resolve_axis_hint(axis)
    return transform(libcarna.base.math.rotation(axis, radians=libcarna.base.math.deg2rad(deg)))


def scale(*factors: float) -> transform:
    if len(factors) == 1:
        factors = (factors[0], factors[0], factors[0])
    elif len(factors) != 3:
        raise ValueError('Scale factor must be a single value, or a tuple of three values.')
    return transform(libcarna.base.math.scaling(*factors))


def translate(x: float, y: float, z: float) -> transform:
    return transform(libcarna.base.math.translation(x, y, z))


def plane(normal: AxisHint, distance: float) -> transform:
    normal = resolve_axis_hint(normal)
    return transform(libcarna.base.math.plane(normal=normal, distance=distance))
