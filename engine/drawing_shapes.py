"""Shape primitives.
"""
from dataclasses import dataclass
from .geometry_types import Point2D


@dataclass
class Line2D:
    """Describe a line in GCS.

    >>> line = Line2D(start=Point2D(0, 1), end=Point2D(2, 3))
    >>> line
    Line2D(start=Point2D(x=0, y=1), end=Point2D(x=2, y=3))
    """
    start: Point2D
    end: Point2D


@dataclass
class Cross45:
    """Describe a cross-hair rotated by 1/8-turn."""
    origin: Point2D                                     # Origin in GCS
    size: float                                         # Span this width in GCS units

    def __post_init__(self):
        r = self.size/2
        self.lines = [
                Line2D(start=Point2D(self.origin.x - r, self.origin.y - r),
                       end=Point2D(self.origin.x + r, self.origin.y + r)
                       ),
                Line2D(start=Point2D(self.origin.x + r, self.origin.y - r),
                       end=Point2D(self.origin.x - r, self.origin.y + r)
                       )
                ]
