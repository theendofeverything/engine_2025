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
    ... m11=2, m12=1,
    ... m21=-4, m22=3)
    >>> m
    Matrix2D(m11=2, m12=1, m21=-4, m22=3)
    >>> print(m)
    |         2          1|
    |        -4          3|
    >>> m.det
    10
    >>> print(m.adj)
    |         3          4|
    |        -1          2|
    >>> print(m.inv)
    |0.30000000000000004                 0.4|
    |               -0.1                 0.2|
    """
    m11: float
    m12: float
    m21: float
    m22: float

    def __str__(self) -> str:
        w = 19  # Right-align each entry to be 19-characters wide
        return (f"|{self.m11:>{w}} {self.m12:>{w}}|\n"
                f"|{self.m21:>{w}} {self.m22:>{w}}|")

    @property
    def det(self) -> float:
        """Determinant of a 2x2 matrix.

        Given the 2x2 column vector matrix M:
            |a   c|
            |b   d|

        M transforms from coordinates (p1, p2) to (g1, g2):
            |a   c|*|p1| = |a*p1 + c*p2| = |g1|
            |b   d| |p2|   |b*p1 + d*p2|   |g2|

        Using orthonormal basis vectors ihat and jhat for (p1, p2), we obtain the basis vectors of
        the (g1, g2) coordinate system:
            ihat = (1, 0),  M*ihat = (a, b)
            jhat = (0, 1),  M*jhat = (c, d)

        As a linear combination of ihat and jhat, the basis vectors of the (g1, g2) coordinate
        system are:
            va = (a*ihat + b*jhat)
            vb = (c*ihat + d*jhat)

        This means matrix M is comprised of the column basis vectors:

              M = |va  vb|  where   va=|a|  and vb=|c|
                                       |b|         |d|

        The determinant of M is the signed magnitude of the wedge product of the basis vectors.
        For the 2x2, it is the bivector obtained from va wedge vb:

            va V vb = (a*ihat + b*jhat) V (c*ihat + d*jhat)

        Note two properties of the wedge product:
            1. The wedge product is distributive with addition: a V (b + c) = (a V b) + (a V c)
            2. And the wedge product has the "zero-torque" property: a V a = 0
        Combining properties 1 and 2, expand (a+b) V (a+b) to obtain the anti-commutative property:
                a V b = -b V a

        Applying zero-torque (a V a = 0) and anti-commutative (a V b = -b V a) properties to the
        wedge product (va V vb), we obtain:

            va V vb = (a*d - b*c)*(ihat V jhat)

        And the determinant of M is (a*d - b*c).
        """
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        return a*d - b*c

    @property
    def adj(self) -> Matrix2D:
        """Adjugate of a 2x2 matrix.

        The adjugate matrix is the transpose of the cofactor matrix.

            adj(M) = tran(cof(M))

        The cofactor matrix is the matrix of minors.

            cof(M) = |minor11 minor12|
                     |minor21 minor22|

        The minor of element i,j is the determinant of the submatrix with row i and column j
        removed, multiplied by -1^(i+j), meaning the signs of the minors is a checkerboard pattern
        of + and - with + signs along the main diagonal.

                 M = | a  b|
                     | c  d|

            cof(M) = | d -c|
                     |-b  a|

        The transpose operation swaps row and column indices, resulting in the adjugate:

            adj(m) = | d -b|
                     |-c  a|
        """
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        return Matrix2D(
                m11=d,  m12=-b,
                m21=-c, m22=a)

    @property
    def inv(self) -> Matrix2D:
        """Inverse of a 2x2 matrix.

        inv(M) = (1/det(M))*adj(M)
        """
        a = self.adj.m11
        b = self.adj.m21
        c = self.adj.m12
        d = self.adj.m22
        s = 1/self.det
        return Matrix2D(
                m11=s*a, m12=s*c,
                m21=s*b, m22=s*d)


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
