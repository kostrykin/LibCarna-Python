from typing import (
    Literal,
)


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
        return tuple(axis)
    else:
        raise ValueError(f'Invalid axis hint: {axis}')
