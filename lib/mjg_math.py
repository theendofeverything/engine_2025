"""Coordinate transform math.
"""


# pylint: disable=too-few-public-methods
class Vec2D:
    """Two-dimensional vector."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"({self.x:0.1f}, {self.y:0.1f})"


def gcs_to_pcs(v: Vec2D) -> Vec2D:
    """Transform vector from game coord sys to pixel coord sys."""
    # Flip y
    v_p = Vec2D(x = v.x, y = -v.y)
    # Scale
    # TODO: how do I want to talk about the scaling vector (zoom)
    # I need to know:
    # - the zoom level, a, which is updated on zoom events
    # - the window size, (w,h), which is updated on window resize events
    a = 5
    v_p.x = a*v_p.x
    v_p.y = a*v_p.y
    # Translate
    # TODO: how do I want to talk about the Translation vector (pan) that
    # locates the GCS origin?
    # I need to know:
    # - the window size, (w,h), which is updated on window resize events
    # - the GCS origin, (origin_g), which is updated on zoom and pan
    origin_g = Vec2D(x=0, y=0)
    w = 30*16
    h = 30*9
    origin_p = Vec2D(origin_g.x + w/2, origin_g.y + h/2)
    v_p.x += origin_p.x
    v_p.y += origin_p.y
    return v_p
