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

Preliminary math definitions:

```python
def mult_vec2h_by_mat2h(h: Vec2DH, mat: Matrix2DH) -> Vec2DH:
    """Multiply 1x3 vector 'h' by 3x3 matrix 'mat'."""
    return Vec2DH(
            h.m1*mat.m11 + h.m2*mat.m21 + h.m3*mat.m31,
            h.m1*mat.m12 + h.m2*mat.m22 + h.m3*mat.m32,
            h.m1*mat.m13 + h.m2*mat.m23 + h.m3*mat.m33
            )


def xfm_vec(v: Vec2D, xfm: Matrix2DH) -> Vec2D:
    # Get the homogeneous-coordinate version of v
    h = Vec2DH(m1=v.x, m2=v.y)
    # Multiply t(v) by the homogeneous-coordinate transformation matrix
    u: Vec2DH = mult_vec2h_by_mat2h(h, xfm)
    # Using homogeneous coordinates, the third element should always be 1
    assert u.m3 == 1
    return Vec2D(x=u.m1, y=u.m2)
```

Coordinate transforms:

```python
    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        return xfm_vec(v, self.xfm_gcs_to_pcs)

    @property
    def xfm_gcs_to_pcs(self) -> Matrix2DH:
        """Matrix that transforms from GCS to PCS."""
        k = self.coord_sys.scale_gcs_to_pcs
        return Matrix2DH(m11=k, m12=0, m21=0, m22=-k, translation=self.coord_sys.translation)
```
