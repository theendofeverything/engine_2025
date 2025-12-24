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
        precision = 0.2
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

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

    def __str__(self) -> str:
        """Vector as a string with precision to two decimal places."""
        precision = 0.2
        return f"({self.x:{precision}f}, {self.y:{precision}f})"

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


# pylint: disable=too-many-instance-attributes
@dataclass
class Matrix2DH:
    """2D affine xfm matrix augmented with homogeneous coordinates for translation.

    >>> gcs_to_pcs = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3))
    >>> gcs_to_pcs
    Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3), m31=0, m32=0, m33=1)
    >>> print(gcs_to_pcs)
    |    5     0      2|
    |    0    -5      3|
    |    0     0      1|
    """
    m11: float  # a
    m12: float  # c
    m21: float  # b
    m22: float  # d
    translation: Vec2D
    m31: float = 0
    m32: float = 0
    m33: float = 1

    def __post_init__(self) -> None:
        self.m13 = self.translation.x
        self.m23 = self.translation.y

    def __str__(self) -> str:
        w = 10  # Right-align each entry to be 10-characters wide
        return (f"|{self.m11:>{w}} {self.m12:>{w}}  {self.m13:>{w}}|\n"
                f"|{self.m21:>{w}} {self.m22:>{w}}  {self.m23:>{w}}|\n"
                f"|{self.m31:>{w}} {self.m32:>{w}}  {self.m33:>{w}}|")


# pylint: disable=too-many-instance-attributes
@dataclass
class Matrix2D:
    """2x2 matrix.

    >>> m = Matrix2D(
    ... m11=11, m12=12,
    ... m21=21, m22=22)
    >>> m
    Matrix2D(m11=11, m12=12, m21=21, m22=22)
    >>> print(m)
    |        11         12|
    |        21         22|
    """
    m11: float
    m12: float
    m21: float
    m22: float

    def __str__(self) -> str:
        w = 10  # Right-align each entry to be 10-characters wide
        return (f"|{self.m11:>{w}} {self.m12:>{w}}|\n"
                f"|{self.m21:>{w}} {self.m22:>{w}}|")


# pylint: disable=too-many-instance-attributes
@dataclass
class Matrix3D:
    """3x3 matrix.

    >>> m = Matrix3D(
    ... m11=11, m12=12, m13=13,
    ... m21=21, m22=22, m23=23,
    ... m31=31, m32=22, m33=33)
    >>> m
    Matrix3D(m11=11, m12=12, m13=13, m21=21, m22=22, m23=23, m31=31, m32=22, m33=33)
    >>> print(m)
    |   11    12     13|
    |   21    22     23|
    |   31    22     33|
    """
    m11: float
    m12: float
    m13: float
    m21: float
    m22: float
    m23: float
    m31: float
    m32: float
    m33: float

    def __str__(self) -> str:
        w = 10  # Right-align each entry to be 10-characters wide
        return (f"|{self.m11:>{w}} {self.m12:>{w}}  {self.m13:>{w}}|\n"
                f"|{self.m21:>{w}} {self.m22:>{w}}  {self.m23:>{w}}|\n"
                f"|{self.m31:>{w}} {self.m32:>{w}}  {self.m33:>{w}}|")
