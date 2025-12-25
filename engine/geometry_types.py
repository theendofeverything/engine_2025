"""Geometry data types: points, vectors, matrices, and their geometry operations.
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
    |  2   1|
    | -4   3|
    >>> m.det
    10
    >>> print(m.adj)
    |  3  -1|
    |  4   2|
    >>> print(m.inv)
    |0.30000000000000004                -0.1|
    |                0.4                 0.2|
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

                 M = | a  c|
                     | b  d|

            cof(M) = | d -b|
                     |-c  a|

        The transpose operation swaps row and column indices, resulting in the adjugate:

            adj(m) = | d -c|
                     |-b  a|
        """
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        return Matrix2D(
                m11=d,  m12=-c,
                m21=-b, m22=a)

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
class Matrix2DH:
    """2D affine xfm matrix augmented with homogeneous coordinates for translation.

    >>> gcs_to_pcs = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3))
    >>> gcs_to_pcs
    Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3), m31=0, m32=0, m33=1)
    >>> print(gcs_to_pcs)
    |    5     0      2|
    |    0    -5      3|
    |    0     0      1|
    >>> m = Matrix2DH(
    ... m11=2, m12=1,
    ... m21=-4, m22=3,
    ... translation=Vec2D(x=16, y=9))
    >>> m
    Matrix2DH(m11=2, m12=1, m21=-4, m22=3, translation=Vec2D(x=16, y=9), m31=0, m32=0, m33=1)
    >>> print(m)
    |         2          1          16|
    |        -4          3           9|
    |         0          0           1|
    >>> m.det
    10
    >>> print(m.adj)
    |         3             -1                  -39|
    |         4              2                  -82|
    |         0              0                   10|
    >>> print(m.inv)
    |0.30000000000000004  -0.1  -3.9000000000000004|
    |       0.4            0.2   -8.200000000000001|
    |         0              0                    1|

    >>> m = Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9))
    >>> m
    Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9), m31=0, m32=0, m33=1)
    >>> print(m)
    |         2          1          16|
    |        -1          3           9|
    |         0          0           1|
    >>> print(m.inv)
    |0.42857142857142855 -0.14285714285714285  -5.571428571428571|
    |0.14285714285714285  0.2857142857142857   -4.857142857142857|
    |                  0                    0                   1|
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

    @property
    def det(self) -> float:
        """Determinant of a 2x2 matrix augmented for homogeneous coordinates.

        Given the special 3x3 matrix:
            |a   c  Tx|
            |b   d  Ty|
            |0   0   1|

        The determinant is the same as the 2x2 column vector matrix M:
            |a   c|
            |b   d|

        See Matrix2D.det

        >>> m = Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9))
        >>> m
        Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9), m31=0, m32=0, m33=1)
        >>> print(m)
        |         2          1          16|
        |        -1          3           9|
        |         0          0           1|
        >>> print(m.det)
        7
        """
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        return a*d - b*c

    @property
    def adj(self) -> Matrix2DH:
        """Adjugate of a 2x2 matrix augmented for homogeneous coordinates.

        The adjugate matrix is the transpose of the cofactor matrix.

            adj(M) = tran(cof(M))

        The cofactor matrix is the matrix of minors.

            cof(M) = |minor11  minor12  minor13|
                     |minor21  minor22  minor23|
                     |minor31  minor32  minor33|

        Given the special 3x3 matrix:
                |a  d  g|   |a   c  Tx|
            M = |b  e  h| = |b   d  Ty|
                |c  f  i|   |0   0   1|

        Notice M contains the 2x2 submatrix N:
             N = |a  c|
                 |b  d|

        The cofactor matrix of M contains the cofactor matrix of N:

            cof(N) = | d -b|
                     |-c  a|

        See Matrix3D.adj for the general cof(M):

            cof(M) = |ei-fh  hc-bi  bf-ec|
                     |gf-di  ai-gc  dc-af|
                     |dh-ge  gb-ah  ae-bd|

        Based on that, we obtain:

                     |         d          -b         0|
            cof(M) = |        -c           a         0|
                     |-dTx + cTy   bTx - aTy   ad - bc|

        The transpose operation swaps row and column indices, resulting in the adjugate:

            adj(m) = |    d     -c  -dTx + cTy|
                     |   -b      a   bTx - aTy|
                     |    0      0     ad - bc|
        """
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        t = Vec2D(x=self.m13, y=self.m23)
        return Matrix2DH(
                m11=d, m12=-c,
                m21=-b, m22=a,
                translation=Vec2D(
                    x=(-d*t.x + c*t.y),
                    y=(b*t.x - a*t.y)
                    ),
                m33=(a*d - b*c)
                )

    @property
    def is_setup_for_column_vectors(self) -> bool:
        """True if matrix is setup for multiplying by column vectors.

        Note: this test only works for 2x2 matrices augmented for homogeneous coordinates.
        """
        return ((self.m31 == 0) and (self.m32 == 0))

    @property
    def inv(self) -> Matrix2DH:
        """Inverse of a 2x2 matrix augmented for homogeneous coordinates.

        inv(M) = (1/det(M))*adj(M)
        """
        assert self.is_setup_for_column_vectors
        # a = self.adj.m11
        # b = self.adj.m21
        # c = self.adj.m12
        # d = self.adj.m22
        # t = Vec2D(x=self.adj.m13, y=self.adj.m23)
        # s = 1/self.det
        # return Matrix2DH(
        #         m11=s*a, m12=s*c,
        #         m21=s*b, m22=s*d,
        #         translation=Vec2D(x=s*t.x, y=s*t.y),
        #         # m33=s*self.adj.m33)   # Do not calculate this: introduces floating-point error
        #         m33=1)                  # It is always 1.
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        det = a*d - b*c
        s = 1/det
        t = self.translation
        return Matrix2DH(m11=s*d, m12=-s*c,
                         m21=-s*b, m22=s*a,
                         translation=Vec2D(
                             x=s*(-d*t.x + c*t.y),
                             y=s*(b*t.x - a*t.y)
                             ))

    def multiply_vec(self, v: Vec2D) -> Vec2D:
        """Multiply matrix by 2D vector in homogeneous coordinates.

        The input vector is 2x1. It is augmented to become 3x1, resulting in multiplication sizes:

            3x3 ● 3x1 = 3x1

        The third element of this product is always 1. An exception is thrown if the third element
        is not 1.

        The third element is dropped and the 2x1 vector is returned.

        self (Matrix2DH):
            2x2 transformation matrix augmented for homogeneous coordinates:
                |a   c  Tx|
                |b   d  Ty|
                |0   0   1|
        v (Vec2D):
            2x1 vector
                |x|
                |y|
            The vector is augmented for homogeneous coordinates:
                |x|
                |y|
                |1|

        Multiplication:
            |a   c  Tx|   |x|   |ax + cy + Tx|
            |b   d  Ty| * |y| = |bx + dy + Ty|
            |0   0   1|   |1|   | 0 +  0 +  1|

        >>> m = Matrix2DH(
        ... m11=2, m12=1,
        ... m21=-4, m22=3,
        ... translation=Vec2D(x=16, y=9))
        >>> v = Vec2D(0, 1)
        >>> m.multiply_vec(v)
        Vec2D(x=17, y=12)

        See CoordinateSystem.xfm() for more explanation and examples.
        """
        h = v.homog
        u = Vec2DH(
                self.m11*h.x1 + self.m12*h.x2 + self.m13*h.x3,
                self.m21*h.x1 + self.m22*h.x2 + self.m23*h.x3,
                self.m31*h.x1 + self.m32*h.x2 + self.m33*h.x3)
        assert u.x3 == 1
        return Vec2D(x=u.x1, y=u.x2)


# pylint: disable=too-many-instance-attributes
@dataclass
class Matrix3D:
    """3x3 matrix.

    >>> m = Matrix3D(
    ... m11=2,  m12=1,  m13=4,
    ... m21=-1, m22=-3, m23=1,
    ... m31=4,  m32=-3, m33=2)
    >>> m
    Matrix3D(m11=2, m12=1, m13=4, m21=-1, m22=-3, m23=1, m31=4, m32=-3, m33=2)
    >>> print(m)
    |         2          1           4|
    |        -1         -3           1|
    |         4         -3           2|
    >>> m.det
    60
    >>> print(m.adj)
    |        -3        -14          13|
    |         6        -12          -6|
    |        15         10          -5|

    >>> v = Vec3D(0, 1, 0)
    >>> m.multiply_vec(v)
    Vec3D(x1=1, x2=-3, x3=-3)


    >>> m = Matrix3D(
    ... m11=2, m12=1, m13=16,
    ... m21=-1, m22=3, m23=9,
    ... m31=0, m32=0, m33=1)
    >>> m
    Matrix3D(m11=2, m12=1, m13=16, m21=-1, m22=3, m23=9, m31=0, m32=0, m33=1)
    >>> print(m)
    |         2          1          16|
    |        -1          3           9|
    |         0          0           1|
    >>> print(m.inv)
    |0.42857142857142855 -0.14285714285714285  -5.571428571428571|
    |0.14285714285714285 0.2857142857142857  -4.857142857142857|
    |       0.0        0.0         1.0|
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

    def multiply_vec(self, v: Vec3D) -> Vec3D:
        """Multiply this 3x3 matrix by 3x1 vector 'v'.
            |m11 m12 m13|   |x1|   |y1|
            |m21 m22 m23| * |x2| = |y2|
            |m31 m32 m33|   |x3|   |y3|
        """
        return Vec3D(
                self.m11*v.x1 + self.m12*v.x2 + self.m13*v.x3,
                self.m21*v.x1 + self.m22*v.x2 + self.m23*v.x3,
                self.m31*v.x1 + self.m32*v.x2 + self.m33*v.x3)

    @property
    def det(self) -> float:
        """Determinant of this 3x3 matrix.

        Given the 3x3 column vector matrix M:
            |a   d   g|
            |b   e   h|
            |c   f   i|

        M transforms from coordinates (p1, p2, p3) to (g1, g2, g3):
            |a   d   g| |p1|   |a*p1 + d*p2 + g*p3|   |g1|
            |b   e   h|*|p2| = |b*p1 + e*p2 + h*p3| = |g2|
            |c   f   i| |p3|   |c*p1 + f*p2 + i*p3|   |g3|

        Using the orthonormal basis ihat, jhat, and khat for (p1, p2, p3), we obtain the basis
        vectors of the (g1, g2, g3) coordinate system:
            ihat = (1, 0, 0),  M*ihat = (a, b, c)
            jhat = (0, 1, 0),  M*jhat = (d, e, f)
            khat = (0, 0, 1),  M*jhat = (g, h, i)

        Decompose basis vectors of M into components over the orthonormal basis ihat, jhat, khat:
            va = (a*ihat + b*jhat + c*khat)
            vb = (d*ihat + e*jhat + f*khat)
            vc = (g*ihat + h*jhat + i*khat)

        This means matrix M is comprised of the column basis vectors:

              M = |va  vb  vc|  where   va=|a|  vb=|d|  vc=|g|
                                           |b|     |e|     |h|
                                           |c|     |f|     |i|

        The determinant of M is the signed magnitude of the wedge product of the basis vectors.
        For the 3x3, it is the trivector obtained from va wedge vb wedge vc:

            va V vb V vc =

                        va             V             vb             V             vc

            (a*ihat + b*jhat + c*khat) V (d*ihat + e*jhat + f*khat) V (g*ihat + h*jhat + i*khat)

        Note two properties of the wedge product:
            1. The wedge product is distributive with addition: a V (b + c) = (a V b) + (a V c)
            2. And the wedge product has the "zero-torque" property: a V a = 0
        Combining properties 1 and 2, expand (a+b) V (a+b) to obtain the anti-commutative property:
                a V b = -b V a

        Applying zero-torque (a V a = 0) and anti-commutative (a V b = -b V a) properties to the
        wedge product (va V vb), we obtain:

            va V vb V vc = (a(ei-fh) + b(fg-di) + c(dh-eg))*(ihat V jhat V khat)

        And the determinant of M is (a(ei-fh) + b(fg-di) + c(dh-eg)).
        """
        a = self.m11
        b = self.m21
        c = self.m31
        d = self.m12
        e = self.m22
        f = self.m32
        g = self.m13
        h = self.m23
        i = self.m33
        return a*(e*i-f*h) + b*(f*g-d*i) + c*(d*h-e*g)

    @property
    def adj(self) -> Matrix3D:
        """Adjugate of this 3x3 matrix.

        The adjugate matrix is the transpose of the cofactor matrix.

            adj(M) = tran(cof(M))

        The cofactor matrix is the matrix of minors.

            cof(M) = |minor11  minor12  minor13|
                     |minor21  minor22  minor23|
                     |minor31  minor32  minor33|

        The minor of element i,j is the determinant of the submatrix with row i and column j
        removed, multiplied by -1^(i+j), meaning the signs of the minors is a checkerboard pattern
        of + and - with + signs along the main diagonal.

                 M = |    a      d      g|
                     |    b      e      h|
                     |    c      f      i|

            cof(M) = |ei-fh  hc-bi  bf-ec|
                     |gf-di  ai-gc  dc-af|
                     |dh-ge  gb-ah  ae-bd|

        The checkboard pattern of + and - is a direct result of the anti-commutative property of the
        wedge product and that elements with odd i+j have 2x2 sub-matrix minors where the order of
        the 2x2 basis vectors is flipped.

        The transpose operation swaps row and column indices, resulting in the adjugate:

            adj(m) = |ei-fh  gf-di  dh-ge|
                     |hc-bi  ai-gc  gb-ah|
                     |bf-ec  dc-af  ae-bd|
        """
        a = self.m11
        b = self.m21
        c = self.m31
        d = self.m12
        e = self.m22
        f = self.m32
        g = self.m13
        h = self.m23
        i = self.m33
        return Matrix3D(
                m11=e*i-f*h, m12=g*f-d*i, m13=d*h-g*e,
                m21=h*c-b*i, m22=a*i-g*c, m23=g*b-a*h,
                m31=b*f-e*c, m32=d*c-a*f, m33=a*e-b*d)

    @property
    def inv(self) -> Matrix3D:
        """Inverse of this 3x3 matrix.

        inv(M) = (1/det(M))*adj(M)

        Exception: 'assert' fails if the determinant is zero.
        """
        assert self.det != 0
        s = 1/self.det
        adj = self.adj
        return Matrix3D(
            m11=s*adj.m11, m12=s*adj.m12, m13=s*adj.m13,
            m21=s*adj.m21, m22=s*adj.m22, m23=s*adj.m23,
            m31=s*adj.m31, m32=s*adj.m32, m33=s*adj.m33)
