"""Entities are things like the Player that track their own state.

TODO: How do I want to set this up?
- Start with making a character that is a wiggling cross.
- Then try a wiggling triangle.
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
"""

from dataclasses import dataclass, field
import random
from .geometry_types import Point2D
from .drawing_shapes import Cross
from .timing import Timing
from .colors import Colors
from .art import Art
from .ui import UIKeys


@dataclass
class AmountExcited:
    """How excited the entity animation is"""
    low: float = 0.004                                  # Low excitement
    high: float = 0.015                                 # High excitement


@dataclass
class Entity:
    """Any character in the game, such as the player.

    API:
        update(timing: Timing, ui_keys: UIKeys):
            If game is not paused, the entity animation updates (if the clocked_event period
            elapsed) and the entity moves (if keys are pressed).
        draw(art: Art):
            Connects lines between all points, including connecting last to first.

    Animations are done by adding a small random wiggle to each point. The animation is clocked by a
    clocked_event (the period of the animation is some whole number of game frame periods).

                            loop()
                             |
                             v
                            update_entities()
                             |
                             v
    Game.Timing ─▶ Entity.update() -> Paused? --┐
                                        |       |
                                       YES      NO
                             ┌─---------┘       |
                             |                  Entity.move()
                             |
                             v
    Game.Art ────▶ Entity.draw()

    >>> entity = Entity(clocked_event_name = "period_3")
    >>> entity
    Entity(clocked_event_name='period_3',
            origin=Point2D(x=..., y=...),
            amount_excited=AmountExcited(low=..., high=...),
            size=...,
            points=[Point2D(...), ...Point2D(...)],
            _is_moving=False)
    """
    clocked_event_name:  str                            # Match name of clocked_events dict key
    origin:             Point2D = Point2D(0, 0)
    amount_excited:     AmountExcited = AmountExcited()
    size:               float = 0.2
    points:             list[Point2D] = field(init=False)
    _is_moving:         bool = False

    def __post_init__(self) -> None:
        # self.points = []
        self.set_initial_points()

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

    def update(self, timing: Timing, ui_keys: UIKeys) -> None:
        """Update entity state based on the Timing -> Ticks and UI -> UIKeys."""
        if not timing.frame_counters["game"].is_paused:
            self.move(ui_keys)
            self.animate(timing)

    @property
    def is_moving(self) -> bool:
        """True if entity is moving."""
        return self._is_moving

    def move(self, ui_keys: UIKeys) -> None:
        """Move the entity based on UI.keys"""
        origin = self.origin
        speed = 0.01
        left = ui_keys.left_arrow
        right = ui_keys.right_arrow
        up = ui_keys.up_arrow
        down = ui_keys.down_arrow
        if left:  origin.x -= speed
        if right: origin.x += speed
        if up:    origin.y += speed
        if down:  origin.y -= speed
        self._is_moving = (left or right or up or down)

    def animate(self, timing: Timing) -> None:
        """Animate the entity.

        Animation speed is clocked by Timing.frame_counters['game'].clocked_events[event_name].
        """
        # Use counter for wiggling animation
        clocked_event = timing.frame_counters["game"].clocked_events[self.clocked_event_name]
        # For a shimmering effect, restore initial points here (on every frame).
        # shimmer = False
        # if shimmer:
        #     self.set_initial_points()
        if clocked_event.is_period:
            self.set_initial_points()
            # This works! Change this to wiggling.
            # origin = self.origin
            # origin.x += 0.01
            if self.is_moving:
                amount_excited = self.amount_excited.high
            else:
                amount_excited = self.amount_excited.low
            for point in self.points:
                point.x += random.uniform(-1*amount_excited, amount_excited)
                point.y += random.uniform(-1*amount_excited, amount_excited)

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        art.draw_lines(self.points)
