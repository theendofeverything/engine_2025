"""Geometry data types: points and vectors.
"""
from __future__ import annotations
from dataclasses import dataclass


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
    """
    x: float
    y: float

    def as_vec(self) -> Vec2D:
        """Consider this point as a vector from (0,0)."""
        return Vec2D(x=self.x, y=self.y)

    def as_tuple(self) -> tuple[float, float]:
        """Return point as (x, y)."""
        return (self.x, self.y)

    def fmt(self, precision: float = 0.1) -> str:
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
    >>> vec.as_tuple()
    (0, 1)
    """
    x: float
    y: float

    def as_point(self) -> Point2D:
        """Consider this vector as a point relative to (0,0)."""
        return Point2D(x=self.x, y=self.y)

    def as_tuple(self) -> tuple[float, float]:
        """Return vector as tuple (x, y)."""
        return (self.x, self.y)

    def fmt(self, precision: float = 0.1) -> str:
        """Vector as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

    @classmethod
    def from_points(cls, start: Point2D, end: Point2D) -> Vec2D:
        """Create a vector from two points: vector = end - start."""
        return cls(x=end.x-start.x,
                   y=end.y-start.y)


@dataclass
class Vec2DH:
    """Two-dimensional vector for work in homogeneous coordinates.

    Create homogeneous-coordinates version of a 2D vector by adding 1 as a third entry
    >>> h = Vec2DH(m1=0, m2=1)
    >>> h
    Vec2DH(m1=0, m2=1, m3=1)
    """
    m1: int | float
    m2: int | float
    m3: int | float = 1


# pylint: disable=too-many-instance-attributes
@dataclass
class Matrix2DH:
    """2D affine xfm matrix augmented with homogeneous coordinates for translation.

    >>> gcs_to_pcs = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3))
    >>> gcs_to_pcs
    Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3), m13=0, m23=0, m33=1)
    >>> print(gcs_to_pcs)
    |    5     0      0|
    |    0    -5      0|
    |    2     3      1|
    """
    m11: float
    m12: float
    m21: float
    m22: float
    translation: Vec2D
    m13: float = 0
    m23: float = 0
    m33: float = 1

    def __post_init__(self) -> None:
        self.m31 = self.translation.x
        self.m32 = self.translation.y

    def __str__(self) -> str:
        return (f"|{self.m11:>5} {self.m12:>5}  {self.m13:>5}|\n"
                f"|{self.m21:>5} {self.m22:>5}  {self.m23:>5}|\n"
                f"|{self.m31:>5} {self.m32:>5}  {self.m33:>5}|")
