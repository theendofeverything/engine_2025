"""Shape primitives.
TODO: rename this to draw_shapes.py
"""
from dataclasses import dataclass
try:
    # from .mjg_math import Point2D
    from mjg_math import Point2D
except ModuleNotFoundError:
    from lib.mjg_math import Point2D


@dataclass
class Line2D:
    """Describe a line in GCS.

    >>> line = Line2D(start=Point2D(0, 1), end=Point2D(2, 3))
    >>> line
    Line2D(start=Point2D(x=0, y=1), end=Point2D(x=2, y=3))
    """
    start: Point2D
    end: Point2D


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    print("Import worked")
