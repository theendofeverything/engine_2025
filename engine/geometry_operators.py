"""Operators on geometry types."""
from typing import cast
from .geometry_types import Vec2D, Vec2DH, Matrix2DH, Vec3D, Matrix3D, Matrix2D


def mult_vec3_by_mat3(v: Vec2DH | Vec3D, mat: Matrix2DH | Matrix3D) -> Vec3D:
    """Multiply 3x3 matrix 'mat' by 3x3 vector 'v'.
        |m11 m12 m13|   |x1|   |y1|
        |m21 m22 m23| * |x2| = |y2|
        |m31 m32 m33|   |x3|   |y3|
    """
    return Vec3D(
            mat.m11*v.x1 + mat.m12*v.x2 + mat.m13*v.x3,
            mat.m21*v.x1 + mat.m22*v.x2 + mat.m23*v.x3,
            mat.m31*v.x1 + mat.m32*v.x2 + mat.m33*v.x3)


def mult_vec2h_by_mat2h(h: Vec2DH, mat: Matrix2DH) -> Vec2DH:
    """Multiply 2D vector and matrix in homogeneous coordinates (augmented to be 1x3 and 3x3).

    This just calls the 3D multiplication function.
    Use this 2D homogeneous coordinate version to:
        - take advantage of static type-checking
        - assert that the third element of the result is 1

    h (Vec2DH):
        2x1 vector augmented for homogeneous coordinates:
            |x|
            |y|
            |1|
    mat (Matrix2DH):
        2x2 transformation matrix augmented for homogeneous coordinates:
            |a   c  Tx|
            |b   d  Ty|
            |0   0   1|

        Since we are working with column vectors, note that the unit vectors of the 2x2: (a,b) and
        (c,d), must be the columns (not the rows):

    Multiplication:
        |a   c  Tx|   |x|   |ax + cy + Tx|
        |b   d  Ty| * |y| = |bx + dy + Ty|
        |0   0   1|   |1|   | 0 +  0 +  1|
    """
    u: Vec2DH
    u = cast(Vec2DH, mult_vec3_by_mat3(h, mat))
    assert u.x3 == 1
    return u


def matrix2dh_is_setup_for_column_vectors(mat: Matrix2DH) -> bool:
    """True if 'mat' is setup for multiplying by column vectors.

    Note: this test only works for 2x2 matrices augmented for homogeneous coordinates.
    """
    return ((mat.m31 == 0) and (mat.m32 == 0))


def mat2dh_inv(mat: Matrix2DH) -> Matrix2DH:
    """Inverse of the special 3x3 matrix that is the 2x2 augmented for homogeneous coordinates.
    Given the special 3x3 matrix:
            |a   c  Tx|
            |b   d  Ty|
            |0   0   1|

    The inverse is much simpler than the general 3x3 inverse.

    >>> m = Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9))
    >>> m
    Matrix2DH(m11=2, m12=1, m21=-1, m22=3, translation=Vec2D(x=16, y=9), m31=0, m32=0, m33=1)
    >>> print(m)
    |         2          1          16|
    |        -1          3           9|
    |         0          0           1|
    >>> print(mat2dh_inv(m))
    |0.42857142857142855 -0.14285714285714285  -5.571428571428571|
    |0.14285714285714285 0.2857142857142857  -4.857142857142857|
    |         0          0           1|
    """
    assert matrix2dh_is_setup_for_column_vectors(mat)
    a = mat.m11
    b = mat.m21
    c = mat.m12
    d = mat.m22
    det = a*d - b*c
    s = 1/det
    t = mat.translation
    return Matrix2DH(m11=s*d, m12=-s*c,
                     m21=-s*b, m22=s*a,
                     translation=Vec2D(
                         x=s*(-d*t.x + c*t.y),
                         y=s*(b*t.x - a*t.y)
                         ))


def mat2d_inv(mat: Matrix2D) -> Matrix2D:
    """Inverse of a 2x2 matrix.

    >>> m = Matrix2D(
    ... m11=2, m12=1,
    ... m21=-1, m22=3)
    >>> m
    Matrix2D(m11=2, m12=1, m21=-1, m22=3)
    >>> mat2d_inv(m)
    Matrix2D(m11=0.42857142857142855, m12=0.14285714285714285,
    m21=-0.14285714285714285, m22=0.2857142857142857)

    inv(M) = det(M)*adj(M)

    Finding the determinant:

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

    Finding the adjugate:

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
    a = mat.m11
    b = mat.m21
    c = mat.m12
    d = mat.m22
    det = a*d - b*c
    s = 1/det
    return Matrix2D(
            m11=s*d,    m12=s*(-b),
            m21=s*(-c), m22=s*a)


def mat3d_inv(mat: Matrix3D) -> Matrix3D:
    """Inverse of a 3x3 matrix.

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
    >>> print(mat3d_inv(m))
    |0.42857142857142855 -0.14285714285714285  -5.571428571428571|
    |0.14285714285714285 0.2857142857142857  -4.857142857142857|
    |       0.0        0.0         1.0|

    inv(M) = det(M)*adj(M)

    Finding the determinant:

        Given the 3x3 column vector matrix M:
            |a   d   g|
            |b   e   h|
            |c   f   i|

        M transforms from coordinates (p1, p2, p3) to (g1, g2, g3):
            |a   d   g| |p1|   |a*p1 + d*p2 + g*p3|   |g1|
            |b   e   h|*|p2| = |b*p1 + e*p2 + h*p3| = |g2|
            |c   f   i| |p3|   |c*p1 + f*p2 + i*p3|   |g3|

        Using orthonormal basis vectors ihat, jhat, and khat for (p1, p2, p3), we obtain the basis
        vectors of the (g1, g2, g3) coordinate system:
            ihat = (1, 0, 0),  M*ihat = (a, b, c)
            jhat = (0, 1, 0),  M*jhat = (d, e, f)
            khat = (0, 0, 1),  M*jhat = (g, h, i)

        As a linear combination of ihat, jhat, and khat, the basis vectors of the (g1, g2, g3)
        coordinate system are:
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

    Finding the adjugate:

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

        The transpose operation swaps row and column indices, resulting in the adjugate:

            adj(m) = |ei-fh  gf-di  dh-ge|
                     |hc-bi  ai-gc  gb-ah|
                     |bf-ec  dc-af  ae-bd|
    """
    a = mat.m11
    b = mat.m21
    c = mat.m31
    d = mat.m12
    e = mat.m22
    f = mat.m32
    g = mat.m13
    h = mat.m23
    i = mat.m33
    det = a*(e*i-f*h) + b*(f*g-d*i) + c*(d*h-e*g)
    s = 1/det
    return Matrix3D(
            m11=s*(e*i-f*h), m12=s*(g*f-d*i), m13=s*(d*h-g*e),
            m21=s*(h*c-b*i), m22=s*(a*i-g*c), m23=s*(g*b-a*h),
            m31=s*(b*f-e*c), m32=s*(d*c-a*f), m33=s*(a*e-b*d))
