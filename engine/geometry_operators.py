"""Geometry operators: coordinate transforms.
"""
from dataclasses import dataclass
from .geometry_types import Vec2D
from .coord_sys import CoordinateSystem


@dataclass
class CoordinateTransform:
    """Coordinate transforms between coordinate systems."""
    coord_sys:              CoordinateSystem

    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        # Return this
        v_p = Vec2D(x=v.x, y=v.y)
        # Flip y
        v_p.y *= -1
        # Scale based on the visible width of GCS at this zoom level
        v_p.x *= self.coord_sys.window_size.x/self.coord_sys.gcs_width
        v_p.y *= self.coord_sys.window_size.x/self.coord_sys.gcs_width
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
        v_g.x *= 1/(self.coord_sys.window_size.x/self.coord_sys.gcs_width)
        v_g.y *= 1/(self.coord_sys.window_size.x/self.coord_sys.gcs_width)
        # Flip y
        v_g.y *= -1
        return v_g
