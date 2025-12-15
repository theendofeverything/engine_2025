"""Geometry operators: coordinate transforms.
"""

from __future__ import annotations
from lib.geometry_types import Vec2D


class CoordinateTransform:
    """Coordinate transforms between coordinate systems."""
    def __init__(self, game: 'Game') -> None:
        self.game = game

    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        game = self.game
        # Return this
        v_p = Vec2D(x=v.x, y=v.y)
        # Flip y
        v_p.y *= -1
        # Scale based on the visible width of GCS at this zoom level
        v_p.x *= game.window_size.x/game.gcs_width
        v_p.y *= game.window_size.x/game.gcs_width
        # Translate pixel coordinate so that screen (0,0) (topleft corner) maps to location of game
        # (0,0) (initially the screen center)
        v_p.x += game.translation.x
        v_p.y += game.translation.y
        return v_p

    def pcs_to_gcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from pixel coord sys to game coord sys."""
        # Return this
        game = self.game
        v_g = Vec2D(x=v.x, y=v.y)
        # Translate pixel coordinate so that location of game (0,0) (initially the screen center)
        # maps to screen (0,0) (topleft corner)
        v_g.x -= game.translation.x
        v_g.y -= game.translation.y
        # Scale
        v_g.x *= 1/(game.window_size.x/game.gcs_width)
        v_g.y *= 1/(game.window_size.x/game.gcs_width)
        # Flip y
        v_g.y *= -1
        return v_g
