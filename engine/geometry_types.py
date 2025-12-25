"""Geometry data types: points and vectors.
"""
from __future__ import annotations
from dataclasses import dataclass

FLOAT_PRINT_PRECISION = 0.2


@dataclass
class Point2D:
    """Two-dimensional point.

    A point is like a vector from the origin, but is not a vector.
    A vector can be translated, a point cannot.

    Create a point from x and y values:
    >>> point = Point2D(x=0, y=1)
    >>> point
    Point2D(x=0, y=1)
    >>> point.as_tuple()
    (0, 1)

    It is often convenient to create a point from a tuple (pygame event positions are tuples):
    >>> point = Point2D.from_tuple((0,1))
    >>> point
    Point2D(x=0, y=1)

    Debug a point:
    >>> print(point)
    (0.00, 1.00)

    Print with higher precision:
    >>> print(point.fmt(0.3))
    (0.000, 1.000)
    """
    x: float
    y: float

    def as_vec(self) -> Vec2D:
        """Consider this point as a vector from (0,0)."""
        return Vec2D(x=self.x, y=self.y)

    def as_tuple(self) -> tuple[float, float]:
        """Return point as (x, y)."""
        return (self.x, self.y)

    def __str__(self) -> str:
        """Point as a string with precision to two decimal places."""
        precision = FLOAT_PRINT_PRECISION
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    def fmt(self, precision: float = FLOAT_PRINT_PRECISION) -> str:
        """Point as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    @classmethod
    def from_tuple(cls, position: tuple[float, float]) -> Point2D:
        """Create a point from a pygame event position (x, y)."""
        return cls(x=position[0], y=position[1])


@dataclass
class Vec2D:
    """Two-dimensional vector.

    >>> vec = Vec2D(x=0, y=1)
    >>> vec
    Vec2D(x=0, y=1)

    Represent as a point:
    >>> vec.as_point()
    Point2D(x=0, y=1)

    Represent as a tuple:
    >>> vec.as_tuple()
    (0, 1)

    Obtain a vector by subtracting two points:
    >>> vec = Vec2D.from_points(start=Point2D(x=1, y=-1), end=Point2D(x=1, y=0))
    >>> vec
    Vec2D(x=0, y=1)

    Obtain the vector in homogeneous coordinates:
    >>> vec.homog
    Vec2DH(x1=0, x2=1, x3=1)

    Debug a vector:
    >>> print(vec)
    (0.00, 1.00)

    Print the vector with higher precision:
    >>> print(vec.fmt(0.3))
    (0.000, 1.000)
    """
    x: float
    y: float

    def as_point(self) -> Point2D:
        """Consider this vector as a point relative to (0,0)."""
        return Point2D(x=self.x, y=self.y)

    def as_tuple(self) -> tuple[float, float]:
        """Return vector as tuple (x, y)."""
        return (self.x, self.y)

    def __str__(self) -> str:
        """Vector as a string with precision to two decimal places."""
        precision = FLOAT_PRINT_PRECISION
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    def fmt(self, precision: float = FLOAT_PRINT_PRECISION) -> str:
        """Vector as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    @classmethod
    def from_points(cls, start: Point2D, end: Point2D) -> Vec2D:
        """Create a vector from two points: vector = end - start."""
        return cls(x=end.x-start.x,
                   y=end.y-start.y)

    @property
    def homog(self) -> Vec2DH:
        """Vector in homogeneous coordinates."""
        return Vec2DH(self.x, self.y)


@dataclass
class Vec2DH:
    """Two-dimensional vector for work in homogeneous coordinates.

    Create homogeneous-coordinates version of a 2D vector by adding 1 as a third entry
    >>> h = Vec2DH(x1=0, x2=1)
    >>> h
    Vec2DH(x1=0, x2=1, x3=1)
    """
    x1: int | float
    x2: int | float
    x3: int | float = 1


@dataclass
class Vec3D:
    """Three-dimensional vector.

    >>> v = Vec3D(x1=1, x2=2, x3=3)
    >>> v
    Vec3D(x1=1, x2=2, x3=3)
    """
    x1: int | float
    x2: int | float
    x3: int | float
