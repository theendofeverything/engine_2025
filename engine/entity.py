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

    >>> entity = Entity(clocked_event_name = "period_3")
    >>> entity
    Entity(clocked_event_name='period_3',
            origin=Point2D(x=0, y=0),
            size=0.2,
            points=[])
    """
    clocked_event_name:  str                            # Match name of clocked_events dict key
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

    def update(self, timing: Timing, ui_keys: UIKeys) -> None:
        """Update entity state based on the Timing -> Ticks and UI -> UIKeys."""
        if not timing.frame_counters["game"].is_paused:
            self.move(ui_keys)
            self.animate(timing)

    def move(self, ui_keys: UIKeys) -> None:
        """Move the entity based on UI.keys"""
        origin = self.origin
        speed = 0.01
        if ui_keys.left_arrow:  origin.x -= speed
        if ui_keys.right_arrow: origin.x += speed
        if ui_keys.up_arrow:    origin.y += speed
        if ui_keys.down_arrow:  origin.y -= speed

    def animate(self, timing: Timing) -> None:
        """Animate the entity.

        Animation speed is clocked by Timing.frame_counters['game'].clocked_events[event_name].
        """
        # Use counter for wigging animation
        clocked_event = timing.frame_counters["game"].clocked_events[self.clocked_event_name]
        origin = self.origin
        # TODO: This works! Change this to wiggling.
        if clocked_event.is_period:
            origin.x += 0.01
        # # For TickCounterWithClock:
        # if counter.clocked:
        #     origin.x += 0.01
