"""Entities are things like the Player that track their own state.

TODO: How do I want to set this up?
- Start with making a character that is a wiggling cross.
- Then try a wiggling triangle.
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
"""

from dataclasses import dataclass, field
from .geometry_types import Point2D
from .drawing_shapes import Cross
from .timing import Timing
from .colors import Colors
from .art import Art
from .ui import UIKeys


@dataclass
class Entity:
    """Any character in the game, such as the player.

    API:
        draw:
        update:

    >>> entity = Entity(tick_counter_name = "period_3")
    >>> entity
    Entity(tick_counter_name='period_3',
            origin=Point2D(x=0, y=0),
            size=0.2,
            points=[])
    """
    tick_counter_name:  str                             # Match name of tick_counter dict key
    origin:             Point2D = Point2D(0, 0)
    size:               float = 0.2
    points:             list[Point2D] = field(init=False)

    def __post_init__(self) -> None:
        self.points = []

    def set_initial_points(self) -> None:
        """Set the artwork vertices back to their non-wiggle values, plus any movement offset."""
        self.points = []
        # TODO: decouple line color from shape description?
        cross = Cross(
                origin=self.origin,
                size=self.size,
                rotate45=True,
                color=Colors.line)
        for line in cross.lines:
            self.points.append(Point2D(line.start.x, line.start.y))
            self.points.append(Point2D(line.end.x, line.end.y))

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS."""
        self.set_initial_points()
        art.draw_lines(self.points)

    def update(self, timing: Timing, keys: UIKeys) -> None:
        """Update entity state based on the Timing -> Ticks and UI -> UIKeys."""
        if not timing.is_paused:
            # TODO: Use counter for wigging animation
            # counter = timing.ticks['game'].counters[self.tick_counter_name]
            self.move(keys)

    def move(self, keys: UIKeys) -> None:
        """Move the entity based on UI.keys"""
        origin = self.origin
        speed = 0.01
        if keys.left_arrow:
            origin.x -= speed
        if keys.right_arrow:
            origin.x += speed
        if keys.up_arrow:
            origin.y += speed
        if keys.down_arrow:
            origin.y -= speed
        # TODO: This works! Change this to wiggling.
        # if counter.is_period:
        #     origin.x += 0.01
        # For TickCounterWithClock:
        # if counter.clocked:
        #     origin.x += 0.01
