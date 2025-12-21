"""Operators on geometry types."""
from typing import cast
from .geometry_types import Vec2DH, Matrix2DH, Vec3D, Matrix3D


def mult_vec3_by_mat3(v: Vec2DH | Vec3D, mat: Matrix2DH | Matrix3D) -> Vec3D:
    """Multiply 3x3 matrix 'mat' by 3x3 vector 'v'.
        |x1 x2 x3| * |m11 m12 m13| = |y1 y2 y3|
                     |m21 m22 m23|
                     |m31 m32 m33|
    """
    return Vec3D(
            v.x1*mat.m11 + v.x2*mat.m21 + v.x3*mat.m31,
            v.x1*mat.m12 + v.x2*mat.m22 + v.x3*mat.m32,
            v.x1*mat.m13 + v.x2*mat.m23 + v.x3*mat.m33
            )


def mult_vec2h_by_mat2h(h: Vec2DH, mat: Matrix2DH) -> Vec2DH:
    """Multiply 2D vector and matrix augmented by homogeneous coordinates to be 1x3 and 3x3.

    This just calls the 3D multiplication function.
    Use this 2D homogeneous coordinate version to:
        - take advantage of static type-checking
        - assert that the third element of the result is 1

    h (Vec2DH):
        1x2 vector augmented for homogeneous coordinates:
            |x y 1|
    mat (Matrix2DH):
        2x2 transformation matrix augmented for homogeneous coordinates:
            |m11 m12 0|
            |m21 m22 0|
            | Tx  Ty 1|

        |x y 1| * |m11 m12 0| = |r t 1|
                  |m21 m22 0|
                  | Tx  Ty 1|
    """
    u: Vec2DH
    u = cast(Vec2DH, mult_vec3_by_mat3(h, mat))
    assert u.x3 == 1
    return u
