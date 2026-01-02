"""Entities are things like the Player that track their own state.

TODO: How do I want to set this up?
- Start with making a character that is a wiggling cross.
- Then try a wiggling triangle.
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
"""

from dataclasses import dataclass
from .geometry_types import Point2D


@dataclass
class Entity:
    """Any character in the game, such as the player."""
    origin: Point2D = Point2D(0, 0)
    size: float = 0.2
