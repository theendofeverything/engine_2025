"""Shape primitives.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from pygame import Color
from .colors import Colors
from .geometry_types import Point2D


class Shape(Enum):
    """Shape primitives for Entity artwork.

    Basic Enum behavior:
    >>> shape = Shape.CROSS
    >>> shape
    <Shape.CROSS: 1>
    >>> print(shape)
    Shape.CROSS
    >>> type(Shape.CROSS)
    <enum 'Shape'>

    Using the Enum to select a shape to instantiate
    TODO: finish figuring out how to use this enum to select a shape!
    shapes = {}
    shapes[Shape.CROSS] = lambda: Cross()
    print(shapes[Shape.CROSS]()) # Need args here!
    """
    CROSS = auto()


@dataclass
class Line2D:
    """Describe a line in GCS.

    >>> line = Line2D(start=Point2D(0, 1), end=Point2D(2, 3))
    >>> line
    Line2D(start=Point2D(x=0, y=1), end=Point2D(x=2, y=3), color=Color(...))
    """
    start: Point2D
    end: Point2D
    color: Color = Colors.line


@dataclass
class Cross:
    """Describe a cross-hair."""
    origin:     Point2D                                     # Origin in GCS
    size:       float                                       # Span this width in GCS units
    rotate45:   bool = False                                # Rotate cross-hair by 1/8th of a turn
    color:      Color = Colors.line                         # Use default line color

    # Instance variables defined in __post_init__()
    lines:      list[Line2D] = field(default_factory=list)  # Two lines make up the cross

    def __post_init__(self) -> None:
        r = self.size/2
        if self.rotate45:
            self.lines = [
                    Line2D(start=Point2D(self.origin.x - r, self.origin.y - r),
                           end=Point2D(self.origin.x + r, self.origin.y + r),
                           color=self.color
                           ),
                    Line2D(start=Point2D(self.origin.x + r, self.origin.y - r),
                           end=Point2D(self.origin.x - r, self.origin.y + r),
                           color=self.color
                           ),
                    ]
        else:
            self.lines = [
                    Line2D(start=Point2D(self.origin.x - r, self.origin.y),
                           end=Point2D(self.origin.x + r, self.origin.y),
                           color=self.color
                           ),
                    Line2D(start=Point2D(self.origin.x, self.origin.y - r),
                           end=Point2D(self.origin.x, self.origin.y + r),
                           color=self.color
                           ),
                    ]
