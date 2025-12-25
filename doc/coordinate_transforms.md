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

# Floating point error

Floating-point errors obfuscate obvious relationships between the matrix and
its inverse.

See https://docs.python.org/3/tutorial/floatingpoint.html

I attempted a quick fix using `float.as_integer_ratio()`:

```python
    def rat(self) -> str:
        """Display fractional values as integer ratios."""
        m11 = self.m11.as_integer_ratio()
        m12 = self.m12.as_integer_ratio()
        m13 = self.m13.as_integer_ratio()
        m21 = self.m21.as_integer_ratio()
        m22 = self.m22.as_integer_ratio()
        m23 = self.m23.as_integer_ratio()
        m31 = self.m31.as_integer_ratio()
        m32 = self.m32.as_integer_ratio()
        m33 = self.m33.as_integer_ratio()
        return (f"|{m11} {m12} {m13}|\n"
                f"|{m21} {m22} {m23}|\n"
                f"|{m31} {m32} {m33}|")
```

But since I am applying this to the matrix after the calculation is already
done, this yields the integer ratio of the floating-point result, not the
integer ratio that is the precise result of the operation.

My temporary solution is to pick, `FLOAT_ROUND_NDIGITS`, a number of digits
after the decimal place that works for the small numbers I use in my doctests,
to use this number for rounding in the `__str__()` methods, and to right-align
the numbers using a width that allows for a single-digit integer portion, the
decimal place, and a space.

```python
FLOAT_ROUND_NDIGITS = 14
FLOAT_PRINT_WIDTH = FLOAT_ROUND_NDIGITS + 3  # Account for "0." and one space
```

For example:

```python
    def __str__(self) -> str:
        w = FLOAT_PRINT_WIDTH  # Right-align each entry to be this wide
        m11 = round(self.m11, FLOAT_ROUND_NDIGITS)
        m12 = round(self.m12, FLOAT_ROUND_NDIGITS)
        m21 = round(self.m21, FLOAT_ROUND_NDIGITS)
        m22 = round(self.m22, FLOAT_ROUND_NDIGITS)
        return (f"|{m11:>{w}} {m12:>{w}}|\n"
                f"|{m21:>{w}} {m22:>{w}}|")

```


TODO: Revisit this and find a way to structure the data using rational numbers
(as pairs of integers) to represent each entry in the matrix. Try the
[fractions](https://docs.python.org/3/library/fractions.html#module-fractions)
module combined with `decimal.Decimal`:
[decimal](https://docs.python.org/3/library/decimal.html#module-decimal).
