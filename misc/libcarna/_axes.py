from typing import (
    Literal,
)

import numpy as np


AxisLiteral = Literal['x', 'y', 'z']
AxisHint = AxisLiteral | tuple[float, float, float] | list[float, float, float]


def resolve_axis_hint(axis: AxisHint) -> tuple[float, float, float]:
    if isinstance(axis, str):
        match axis:
            case 'x':
                return (1, 0, 0)
            case 'y':
                return (0, 1, 0)
            case 'z':
                return (0, 0, 1)
            case _:
                raise ValueError(f'Invalid axis hint: {axis}')
    elif len(axis) == 3:
        axis = tuple(axis)
        axis_norm = np.linalg.norm(axis)
        if axis_norm == 0:
            raise ValueError('Axis hint cannot be a zero vector.')
        else:
            return tuple(np.divide(axis, axis_norm))
    else:
        raise ValueError(f'Invalid axis hint: {axis}')
