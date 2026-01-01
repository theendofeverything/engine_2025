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

### Columns are the basis vectors

A 2x2 coordinate transformation matrix, A, is comprised of column vectors (a,b)
and (c,d).

    |v1   v2| = |a   c|
                |b   d|

Multiplication by column vector (e1, e2) transforms the colum vector
from e-space to f-space as (f1, f2), meaning that the matrix multiplication
returns the e-space coordinates of the same coordinate in f-space.

    (e1, e2) to (f1, f2):
        |a   c|*|e1| = |ae1 + ce2| = |f1|
        |b   d| |e2|   |be1 + de2|   |f2|

For example, using (e1, e2) = (1, 0) yields the first column of A.

    |a   c|*|1| = |a| = |v1|
    |b   d| |0|   |b|

So, f-space (1, 0) is (a, b) in e-space coordinates.
And f-space (0, 1) is (c, d) in e-space coordinates.

The above multiplies the matrix by a *single* vector from the orthonormal
basis to obtain a *single* basis vector.

Alternatively, we can express *all* vectors in the orthonormal basis as a
row-vector and multiply in one shot to obtain *all* (two) basis vectors:

    |i  j| * |a   c| = |ai + bj| = |v1|
             |b   d|   |ci + dj| = |v2|

    where i and j are the orthonormal vectors i-hat and j-hat

The above shows a decomposition of the column-vectors of A into components over
an orthonormal basis.

### Determinant is the unit cell scaling factor

In addition to transforming the basis vectors of e-space to the columns of the
matrix, the coordinate transform (multiplication by the matrix) also scales the
e-space unit cell to the f-space unit cell. This scaling factor is the ratio of
the *signed* areas of the two unit cells.

Of course we can draw the unit cell on paper (and this is a good exercise). But
we also want an algebraic way of expressing the unit cell. The particular shape
of the cell is unimportant, only the signed magnitude matters (as this is the
scaling factor between the two coordinate systems).

This signed magnitude is obtained by taking the wedge product of the basis
vectors. The wedge product does not yield a vector. In two dimensions we get a
new geometric object called a **bivector**. In three dimensions we get a
**trivector**. In the same way that a vector is a directed line segment, a
bivector is a directed area segment, and a trivector is a directed volume
segment. Although the bivector is not any one specific parallelogram, it can be
visualized as the parallelogram formed by the two basis vectors from a 2x2
matrix. Similarly, the trivector can be visualized as the parallelipiped formed
by the three basis vectors from a 3x3 matrix.

Considering just two dimensions, say the orthonormal basis vectors are e1 and
e2. Then the wedge product e1 ∧ e2 is the unit bivector. Say the basis vectors
of some space (like f-space) are v1 and v2. We can decompose this wedge product
v1 ∧ v2 into the unit bivector e1 ∧ e2 scaled by the signed magnitude (ad - bc)
where v1 = (a, b) and v2 = (c, d).

This signed magnitude is the determinant of the matrix that transforms the
e1, e2 orthonormal vectors to the v1, v2 basis vectors. I will derive the result
ad - bc in the next section.

In three dimensions, the wedge product of the basis vectors v1 ∧ v2 ∧ v3 yields
the trivector with the signed magnitude of the parallelipiped formed by these
three basis vectors. We can decompose v1 ∧ v2 ∧ v3 into the unit trivector
e1 ∧ e2 ∧ e3 scaled by the signed magnitude (a(ei-fh) + b(fg-di) + c(dh-eg)). I
will derive this result in the next section too.

### Matrix inversion

The operation of matrix inversion is decomposed into two steps.

First, find the determinant of the original matrix and take the inverse of the
determinant. This is the scaling factor that converts the signed area of the
unit cell in f-space back to the signed area of the unit cell in e-space.

Second, find the adjugate of the original matrix. The adjugate is the tranpose
of the cofactor matrix. The cofactor matrix is the matrix of minors multiplied
by -1 for odd row+column or +1 for even. This results in a checkerboard pattern
of + and - signs. The rationale for this + and - pattern is easier to observe
in the 3x3 cofactor matrix, but I will start with the 2x2 case because I find
it easier to understand all the steps involved in taking the inverse of a 2x2.

The algorithm for finding the inverse is easier to study in the case of the 2x2
because the minors are 1x1 matrices and because the adjugate is easily obtained
by the high-school algebra methods of solving two equations with two unknowns.

Before moving onto the 3x3 case, note the properties of the wedge product:

1. The property of "zero-torque": a vector wedge any scalar multiple of itself
   is the zero bivector
2. The distribute property
3. Combining properties 1 and 2 by inspecting (a + b) ∧ (a + b) yields the anti-commutative property

In the 3x3 case, the bivector becomes a trivector. The wedge product of the
basis vectors, (a + d + g) ∧ (b + e + h) ∧ (c + f + i) only has six terms: the
"zero-torque" property makes all other terms zero. In this way, geometric
algebra (the wedge product) makes the determinant of a 3x3 easy to derive from
scratch.

The adjugate is more tedious to obtain for a 3x3, but is not too much work. In
the process of calculating the minors of the 3x3, it becomes apparent that the
sub-matrix determinant calculations are wedge products and that the alternative
+ and - signs comes about from the order of the basis vectors in the wedge
product: when the order is reversed, the sign is negative.

Finally, note that the calculation in the case of a 2x2 augmented for
homogeneous coordinates is much simpler to calculate because the third row of
the matrix is (0 0 1).

# Matrix inversion in Python

## Preliminary math definitions

For work in 2D:

```python
@dataclass
class Vec2DH:
    x1: int | float
    x2: int | float
    x3: int | float = 1


@dataclass
class Vec2D:
    x: float
    y: float

    @property
    def homog(self) -> Vec2DH:
        """Vector in homogeneous coordinates."""
        return Vec2DH(self.x, self.y)


@dataclass
class Matrix2DH:
    m11: float  # a
    m12: float  # c
    m21: float  # b
    m22: float  # d
    translation: Vec2D
    m31: float = 0
    m32: float = 0
    m33: float = 1

    def multiply_vec(self, v: Vec2D) -> Vec2D:
        h = v.homog
        u = Vec2DH(
                self.m11*h.x1 + self.m12*h.x2 + self.m13*h.x3,
                self.m21*h.x1 + self.m22*h.x2 + self.m23*h.x3,
                self.m31*h.x1 + self.m32*h.x2 + self.m33*h.x3)
        assert u.x3 == 1
        return Vec2D(x=u.x1, y=u.x2)

    @property
    def is_setup_for_column_vectors(self) -> bool:
        return ((self.m31 == 0) and (self.m32 == 0))

    def inv(self) -> Matrix2DH:
        assert self.is_setup_for_column_vectors
        a = self.m11
        b = self.m21
        c = self.m12
        d = self.m22
        det = a*d - b*c
        assert det != 0
        s = 1/det
        t = self.translation
        return Matrix2DH(m11=s*d, m12=-s*c,
                         m21=-s*b, m22=s*a,
                         translation=Vec2D(
                             x=s*(-d*t.x + c*t.y),
                             y=s*(b*t.x - a*t.y)
                             ))
```

For work in 3-D (TODO: add homogeneous coordinates):

```python
@dataclass
class Vec3D:
    x1: int | float
    x2: int | float
    x3: int | float


@dataclass
class Matrix3D:
    ...
    def multiply_vec(self, v: Vec3D) -> Vec3D:
        return Vec3D(
                self.m11*v.x1 + self.m12*v.x2 + self.m13*v.x3,
                self.m21*v.x1 + self.m22*v.x2 + self.m23*v.x3,
                self.m31*v.x1 + self.m32*v.x2 + self.m33*v.x3)

    @property
    def det(self) -> float:
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
        assert self.det != 0
        s = 1/self.det
        adj = self.adj
        return Matrix3D(
            m11=s*adj.m11, m12=s*adj.m12, m13=s*adj.m13,
            m21=s*adj.m21, m22=s*adj.m22, m23=s*adj.m23,
            m31=s*adj.m31, m32=s*adj.m32, m33=s*adj.m33)
```

## Coordinate transforms

I make a list of the coordinate transforms in `_Matrices`. These get their
dynamic values from `CoordinateSystem`, which is free to update on every
iteration of the game loop as the user moves the camera.

```python
class _Matrices:
    """Private class to namespace matrices used by CoordinateSystem."""
    coord_sys: CoordinateSystem

    @property
    def gcs_to_pcs(self) -> Matrix2DH:
        k = self.coord_sys.scaling.gcs_to_pcs
        return Matrix2DH(m11=k, m12=0, m21=0, m22=-k, translation=self.coord_sys.translation)

    @property
    def pcs_to_gcs(self) -> Matrix2DH:
        return self.gcs_to_pcs.inv
```

I use those matrices in `CoordinateSystem` to give the game access to a
particular matrix (e.g., as `mat.gcs_to_pcs`) and a `xfm()` method for using
that matrix to transform a vector.

```python
class CoordinateSystem:
    ...
    mat:         _Matrices = field(init=False)          # Coord system xfm matrices
    ...

    @property
    def translation(self) -> Vec2D:
        return Vec2D(x=self.pcs_origin.x + self.panning.vector.x,
                     y=self.pcs_origin.y + self.panning.vector.y)

    @staticmethod
    def xfm(v: Vec2D, mat: Matrix2DH) -> Vec2D:
        return mat.multiply_vec(v)
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
