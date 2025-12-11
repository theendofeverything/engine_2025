"""Shape primitives.
"""
from dataclasses import dataclass
try:
    from mjg_math import Point2D
except ModuleNotFoundError:
    from lib.mjg_math import Point2D


@dataclass
class Line2D:
    """Describe a line in GCS."""
    start: Point2D
    end: Point2D


if __name__ == '__main__':
    line = Line2D(start=Point2D(0, 1), end=Point2D(2, 3))
    print(f"{line}")
