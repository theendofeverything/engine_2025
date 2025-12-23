# High-school algebra version

```python
    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
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
```

# Matrix algebra version

## Background

A 2x2 coordinate transformation matrix, A, is comprised of column vectors (a,b)
and (c,d). Multiplication by column vector (e1, e2) transforms the colum vector
from e-space to f-space as (f1, f2), meaning that it tells us the e-space
coordinates of the f-space vector.

For example, using (e1, e2) = (1, 0) yields the first column of A. The first
column of A is, therefore, f1, the e-space coordinates of the unit vector (1,
0) in f-space.

The transformation scales the e-space unit cell, defined by the
bivector wedge product e1 v e2, to the bivector f1 v f2.

The scalar component of the wedge product of the basis vectors is the
determinant of the matrix that transforms unit vectors to those basis vectors.

The operation of matrix inversion is decomposed into two steps. First, find the
determinant of the original matrix and take its inverse. This is the scaling
factor that converts the signed area of the unit cell in f-space back to the
signed area of the unit cell in e-space. Second, find the adjugate of the
original matrix. The adjugate is tranpose of the cofactor matrix. The cofactor
matrix is the matrix of minors multiplied by -1 for odd row+column or +1 for
even. This mechanism is easier to study in the case of the 2x2 because the
minors are 1x1 matrices and because the adjugate is easily obtained by the
high-school algebra methods of solving two equations with two unknowns.

Before moving onto the 3x3 case, note the properties of the wedge product:

1. The property of "zero-torque": a vector wedge any scalar multiple of itself
   is the zero bivector
2. The distribute property
3. Combining properties 1 and 2 by inspecting (a + b) v (a + b) yields the anti-commutative property

In the 3x3 case, the bivector becomes a trivector. The wedge product of the
basis vectors, (a + d + g) v (b + e + h) v (c + f + i) only has six terms: the
"zero-torque" property makes all other terms zero. In this way, geometric
algebra (the wedge product) makes the determinant of a 3x3 is easy to derive from scratch.

The adjugate is more tedious to obtain, but is not too much work.

Finally, note that the calculation in the case of a 2x2 augmented for
homogeneous coordinates is much simpler to calculate because the third row of
the matrix is (0 0 1).

## Preliminary math definitions

```python
def mult_vec3_by_mat3(v: Vec2DH | Vec3D, mat: Matrix2DH | Matrix3D) -> Vec3D:
    """Multiply 3x3 matrix 'mat' by 3x3 vector 'v'."""
    return Vec3D(
            v.x1*mat.m11 + v.x2*mat.m12 + v.x3*mat.m13,
            v.x1*mat.m21 + v.x2*mat.m22 + v.x3*mat.m23,
            v.x1*mat.m31 + v.x2*mat.m32 + v.x3*mat.m33)


def mult_vec2h_by_mat2h(h: Vec2DH, mat: Matrix2DH) -> Vec2DH:
    """Multiply 2D vector and matrix in homogeneous coordinates (augmented to be 1x3 and 3x3)."""
    u: Vec2DH
    u = cast(Vec2DH, mult_vec3_by_mat3(h, mat))
    assert u.x3 == 1
    return u
```

## Coordinate transforms

```python
class CoordinateSystem:
    ...
    @staticmethod
    def xfm(v: Vec2D, mat: Matrix2DH) -> Vec2D:
        # Get the homogeneous-coordinate version of v
        h = Vec2DH(x1=v.x, x2=v.y)
        # Multiply h by the homogeneous-coordinate transformation matrix
        u: Vec2DH = mult_vec2h_by_mat2h(h, mat)
        return Vec2D(x=u.x1, y=u.x2)

    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        return xfm_vec(v, self.xfm_gcs_to_pcs)

    @property
    def gcs_to_pcs(self) -> Matrix2DH:
        """Matrix that transforms from GCS to PCS."""
        k = self.scale_gcs_to_pcs
        return Matrix2DH(m11=k, m12=0, m21=0, m22=-k, translation=self.translation)

    @property
    def pcs_to_gcs(self) -> Matrix2DH:
        """Matrix that transforms from PCS to GCS."""
        return mat2dh_inv(self.gcs_to_pcs)
```
