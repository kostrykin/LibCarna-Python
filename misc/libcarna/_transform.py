import numpy as np


class transform:

    def __init__(self, mat: np.ndarray):
        self.mat = mat
    
    def point(self, xyz: np.ndarray = np.zeros(3)) -> np.ndarray:
        return (self.mat @ np.array([*xyz, 1.0]))[:3]
    
    def intpoint(self, *args, **kwargs) -> tuple[int, int, int]:
        return tuple(self.point(*args, **kwargs).round().astype(int))
    
    def direction(self, xyz: np.ndarray = np.zeros(3)) -> np.ndarray:
        return self.mat @ np.array([*xyz, 0.0])
