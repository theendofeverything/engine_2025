"""Entities are things like the Player that track their own state.

TODO: How do I want to set this up?
- Start with making a character that is a wiggling cross.
- Then try a wiggling triangle.
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
"""

from dataclasses import dataclass
from .geometry_types import Point2D
from .timing import Timing


@dataclass
class Entity:
    """Any character in the game, such as the player."""
    tick_counter_name:  str                             # Match name of tick_counter dict key
    origin:             Point2D = Point2D(0, 0)
    size:               float = 0.2

    def update(self, timing: Timing) -> None:
        """Update entity state based on the Timing -> Ticks."""
        if not timing.is_paused:
            counter = timing.ticks['game'].counters[self.tick_counter_name]
            origin = self.origin
            # For TickCounterWithClock:
            # if counter.clocked:
            #     origin.x += 0.01
            if counter.is_period:
                origin.x += 0.01
