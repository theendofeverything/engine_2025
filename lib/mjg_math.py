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
    # Return this
    v_p = Vec2D(x=v.x, y=v.y)
    # Flip y
    v_p.y *= -1
    # Scale
    # TODO: how do I want to talk about the scaling vector (zoom)
    # I need to know:
    # - the zoom level, a, which is updated on zoom events
    # - the window size, (w,h), which is updated on window resize events
    w = 30*16
    h = 30*9
    a = w/2
    v_p.x *= a
    v_p.y *= a
    # Translate pixel coordinate so that screen topleft maps to screen center
    # TODO: how do I want to talk about the Translation vector (pan) that
    # locates the GCS origin?
    # I need to know:
    # - the window size, (w,h), which is updated on window resize events
    # - the GCS origin, (origin_g), which is updated on zoom and pan
    translation = Vec2D(w/2, h/2)
    v_p.x += translation.x
    v_p.y += translation.y
    return v_p


def pcs_to_gcs(v: Vec2D) -> Vec2D:
    """Transform vector from pixel coord sys to game coord sys."""
    # Return this
    v_g = Vec2D(x=v.x, y=v.y)
    # Translate pixel coordinate so that screen center maps to screen topleft
    w = 30*16
    h = 30*9
    translation = Vec2D(w/2, h/2)
    v_g.x -= translation.x
    v_g.y -= translation.y
    # Scale
    v_g.x *= 1/(w/2)
    v_g.y *= 1/(w/2)
    # Flip y
    v_g.y *= -1
    return v_g
