"""Operators on geometry types."""
from typing import cast
from .geometry_types import Vec2D, Vec2DH, Matrix2DH, Vec3D, Matrix3D


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
