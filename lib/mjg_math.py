"""Coordinate transform math.
"""
from dataclasses import dataclass


@dataclass
class Point2D:
    """Two-dimensional point.

    A point is like a vector from the origin, but is not a vector.
    A vector can be translated, a point cannot.
    """
    x: float
    y: float

    def as_tuple(self) -> tuple:
        """Return point as (x, y)."""
        return (self.x, self.y)


@dataclass
class Vec2D:
    """Two-dimensional vector."""
    x: float
    y: float

    def as_tuple(self) -> tuple:
        """Return vector as tuple (x, y)."""
        return (self.x, self.y)


if __name__ == '__main__':
    point = Point2D(x=0, y=1)
    print(f"{point}")
    print(f"{point.as_tuple()}")
    vec = Vec2D(x=0, y=1)
    print(f"{vec}")
    print(f"{vec.as_tuple()}")
