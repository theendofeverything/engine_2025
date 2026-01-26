"""Geometry data types: points and vectors.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import sys
import math

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
        """Point as string with two decimal places (default: FLOAT_PRINT_PRECISION)."""
        return self.fmt(FLOAT_PRINT_PRECISION)

    def fmt(self, precision: float) -> str:
        """Point as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    @classmethod
    def from_tuple(cls, position: tuple[float, float]) -> Point2D:
        """Create a point from a pygame event position (x, y)."""
        return cls(x=position[0], y=position[1])


@dataclass
class DirectedLineSeg2D:
    """Two-dimensional directed line segment."""
    start: Point2D = field(default_factory=lambda: Point2D(x=0.0, y=0.0))
    end: Point2D = field(default_factory=lambda: Point2D(x=0.0, y=0.0))

    def parametric_point(self, param: float = 0.5) -> Point2D:
        """Return the Point2D = start + param*(end - start)"""
        start = self.start
        end = self.end
        return Point2D(
                x=start.x + param*(end.x - start.x),
                y=start.y + param*(end.y - start.y))


@dataclass
class Vec2D:
    """Two-dimensional vector.

    >>> vec = Vec2D(x=3, y=4)
    >>> vec
    Vec2D(x=3, y=4)

    Represent as a point:
    >>> vec.as_point()
    Point2D(x=3, y=4)

    Represent as a tuple:
    >>> vec.as_tuple()
    (3, 4)

    Get the magnitude:
    >>> vec.mag
    5.0

    Obtain the unit vector:
    >>> vec.to_unit_vec()
    Vec2D(x=0.6, y=0.8)

    Scale the vector by 2:
    >>> vec.scale_by(2)
    >>> vec
    Vec2D(x=6, y=8)
    >>> vec.mag
    10.0

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

    @property
    def mag(self) -> float:
        """Return the magnitude of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def mag_never_zero(self) -> float:
        """Return the magnitude of the vector. If 0, return smallest float."""
        return max(math.sqrt(self.x**2 + self.y**2), sys.float_info.min)

    def to_unit_vec(self) -> Vec2D:
        """Return the unit vector."""
        return Vec2D(
                x=self.x/self.mag_never_zero,
                y=self.y/self.mag_never_zero)

    def scale_by(self, k: float) -> None:
        """Scale the vector by k."""
        self.x *= k
        self.y *= k

    def __str__(self) -> str:
        """Vector as string with two decimal places (default: FLOAT_PRINT_PRECISION)."""
        return self.fmt(FLOAT_PRINT_PRECISION)

    def fmt(self, precision: float) -> str:
        """Vector as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    @classmethod
    def from_points(cls, start: Point2D, end: Point2D) -> Vec2D:
        """Create a vector from two points: vector = end - start."""
        return cls(x=end.x-start.x,
                   y=end.y-start.y)

    @classmethod
    def from_tuple(cls, xy: tuple[int | float, int | float]) -> Vec2D:
        """Create a vector from tuple (x, y)."""
        return cls(x=xy[0], y=xy[1])

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
