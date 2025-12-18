"""Shape primitives.
"""
from dataclasses import dataclass, field
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
class Cross:
    """Describe a cross-hair."""
    origin:     Point2D                                     # Origin in GCS
    size:       float                                       # Span this width in GCS units
    rotate45:   bool = False                                # Rotate cross-hair by 1/8th of a turn
    lines:      list[Line2D] = field(default_factory=list)  # Two lines make up the cross

    def __post_init__(self) -> None:
        r = self.size/2
        if self.rotate45:
            self.lines = [
                    Line2D(start=Point2D(self.origin.x - r, self.origin.y - r),
                           end=Point2D(self.origin.x + r, self.origin.y + r)
                           ),
                    Line2D(start=Point2D(self.origin.x + r, self.origin.y - r),
                           end=Point2D(self.origin.x - r, self.origin.y + r)
                           )
                    ]
        else:
            self.lines = [
                    Line2D(start=Point2D(self.origin.x - r, self.origin.y),
                           end=Point2D(self.origin.x + r, self.origin.y)
                           ),
                    Line2D(start=Point2D(self.origin.x, self.origin.y - r),
                           end=Point2D(self.origin.x, self.origin.y + r)
                           )
                    ]
