from typing import (
    Callable,
    Iterable,
)

import numpy as np

import libcarna
from ._axes import AxisHint, resolve_axis_hint



class animation:
    """
    Create an animation that can be rendered.

    Arguments:
        step_functions: List of functions that are called for each frame of the animation. Each function is called with
            a single argument `t`, which is a float in the range (0, 1]. The function should modify the scene in place.
            To obtain a smooth eternal animation, the scene should be in it's initial state at `t=1`.
        n_frames: Number of frames to be rendered.
    """

    def __init__(self, step_functions: list[Callable[[float], None]], n_frames: int = 25):
        self.step_functions = step_functions
        self.n_frames = n_frames

    def render(self, r: 'libcarna.renderer', *args, **kwargs) -> Iterable[np.ndarray]:
        for t in np.linspace(1, 0, num=self.n_frames, endpoint=False)[::-1]:
            for step in self.step_functions:
                step(t)
            yield r.render(*args, **kwargs)

    @staticmethod
    def rotate_local(spatial: libcarna.base.Spatial, axis: AxisHint = 'y') -> Callable[[float], None]:
        """
        Create a step function for rotating an object's local coordinate system.
        """
        axis = resolve_axis_hint(axis)
        base_transform = spatial.local_transform
        def step(t: float):
            spatial.local_transform = libcarna.math.rotation(axis, radians=2 * np.pi * t) @ base_transform
        return step
    
    @staticmethod
    def swing_local(spatial: libcarna.base.Spatial, axis: AxisHint = 'y', amplitude: float = np.pi / 4) -> Callable[[float], None]:
        """
        Create a step function for swinging an object's local coordinate system.
        """
        axis = resolve_axis_hint(axis)
        base_transform = spatial.local_transform
        def step(t: float):
            radians = amplitude * np.sin(2 * np.pi * t)
            spatial.local_transform = libcarna.math.rotation(axis, radians=radians) @ base_transform
        return step
    
    @staticmethod
    def bounce_local(spatial: libcarna.base.Spatial, axis: AxisHint, amplitude: float = 1.0) -> Callable[[float], None]:
        """
        Create a step function for bouncing an object along a given axis.
        """
        axis = resolve_axis_hint(axis)
        base_transform = spatial.local_transform
        def step(t: float):
            offset = np.multiply(axis, amplitude * np.sin(2 * np.pi * t))
            spatial.local_transform = libcarna.math.translation(offset) @ base_transform
        return step
