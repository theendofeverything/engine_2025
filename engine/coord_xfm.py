"""Coordinate transforms operate on geometry types.
"""
from dataclasses import dataclass
from .geometry_types import Vec2D, Vec2DH, Matrix2DH
from .geometry_operators import mult_vec2h_by_mat2h
from .coord_sys import CoordinateSystem


def xfm_vec(v: Vec2D, xfm: Matrix2DH) -> Vec2D:
    """Xfm 'v' to a new coordinate system by matrix multiplication of 'v' and 'xfm'.

    v:
        v = |x|
            |y|

        transpose(v) = t(v) = |x y|

        Using homogeneous-coordinates, t(v) = |x y 1|

    xfm:
        The xfm is a 2x2 augmented with a translation vector to become a 3x3:

            xfm = |m11 m12   0|
                  |m21 m22   0|
                  | Tx  Ty   1|

            where |Tx Ty| is the vector that translates the origin between coordinate systems

    The operation performed by xfm_vec() is t(v) * xfm:

        |x y 1| * |m11 m12   0| = |x*m11 + y*m21 + Tx, x*m12 + y*m22 + Ty, 1|
                  |m21 m22   0|
                  | Tx  Ty   1|

    It easier to read the product as the transpose:

        |x*m11 + y*m21 + Tx|
        |x*m12 + y*m22 + Ty|
        |    0 +     0 +  1|

    We only needed homogeneous coordinates to include translation in the transform.
    Return just the 2D vector (discarding the third element, 1):

        |x*m11 + y*m21 + Tx|
        |x*m12 + y*m22 + Ty|

    Example 1: Leave the origin where it is and just scale.
    >>> v = Vec2D(x=1, y=1)
    >>> v
    Vec2D(x=1, y=1)
    >>> xfm = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=0, y=0))
    >>> print(xfm)
    |    5     0      0|
    |    0    -5      0|
    |    0     0      1|

    >>> xfm_vec(v, xfm)
    Vec2D(x=5, y=-5)

    Example 2: Now just translate the origin and don't change anything else.
    >>> v = Vec2D(x=1, y=1)
    >>> v
    Vec2D(x=1, y=1)
    >>> xfm = Matrix2DH(m11=1, m12=0, m21=0, m22=1, translation=Vec2D(x=2, y=3))
    >>> print(xfm)
    |    1     0      0|
    |    0     1      0|
    |    2     3      1|

    >>> xfm_vec(v, xfm)
    Vec2D(x=3, y=4)

    Example 3: Scale and translate.
    >>> v = Vec2D(x=1, y=1)
    >>> v
    Vec2D(x=1, y=1)
    >>> xfm = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3))
    >>> print(xfm)
    |    5     0      0|
    |    0    -5      0|
    |    2     3      1|

    >>> xfm_vec(v, xfm)
    Vec2D(x=7, y=-2)
    """
    # Get the homogeneous-coordinate version of v
    h = Vec2DH(x1=v.x, x2=v.y)
    # Multiply t(v) by the homogeneous-coordinate transformation matrix
    u: Vec2DH = mult_vec2h_by_mat2h(h, xfm)
    return Vec2D(x=u.x1, y=u.x2)


@dataclass
class CoordinateTransform:
    """Coordinate transforms between coordinate systems."""
    coord_sys:              CoordinateSystem

    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        return xfm_vec(v, self.xfm_gcs_to_pcs)

    @property
    def xfm_gcs_to_pcs(self) -> Matrix2DH:
        """Matrix that transforms from GCS to PCS."""
        k = self.coord_sys.scale_gcs_to_pcs
        return Matrix2DH(m11=k, m12=0, m21=0, m22=-k, translation=self.coord_sys.translation)

    def old_gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        # Return this
        v_p = Vec2D(x=v.x, y=v.y)
        # Flip y
        v_p.y *= -1
        # Scale based on the visible width of GCS at this zoom level
        v_p.x *= self.coord_sys.scale_gcs_to_pcs
        v_p.y *= self.coord_sys.scale_gcs_to_pcs
        # Translate pixel coordinate so that screen (0,0) (topleft corner) maps to location of game
        # (0,0) (initially the screen center)
        v_p.x += self.coord_sys.translation.x
        v_p.y += self.coord_sys.translation.y
        return v_p

    def pcs_to_gcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from pixel coord sys to game coord sys."""
        # Return this
        v_g = Vec2D(x=v.x, y=v.y)
        # Translate pixel coordinate so that location of game (0,0) (initially the screen center)
        # maps to screen (0,0) (topleft corner)
        v_g.x -= self.coord_sys.translation.x
        v_g.y -= self.coord_sys.translation.y
        # Scale
        v_g.x *= self.coord_sys.scale_pcs_to_gcs
        v_g.y *= self.coord_sys.scale_pcs_to_gcs
        # Flip y
        v_g.y *= -1
        return v_g
