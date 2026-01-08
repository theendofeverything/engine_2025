"""Entities are things like the Player that track their own state.

TODO: Separate my "player" and "cross" entities (they overlap right now)
TODO: How do I want to set up entity artwork?
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
- [x] Start with making a character that is a wiggling cross.
- [ ] Then try a wiggling triangle.
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
    low: float = 0.010                                  # Low excitement
    high: float = 0.050                                 # High excitement


@dataclass
class Movement:
    """Entity movement data: speed and up/down/left/right, and whether or not it is moving."""
    speed:  float = 0.01
    up:     bool = False
    down:   bool = False
    left:   bool = False
    right:  bool = False
    is_moving:  bool = False


# TODO: Create "Player" by checking entity name or create a new class for Player that uses Entity by
# composition?
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
    clocked_event_name: str = "every_frame"             # Match name of clocked_events dict key
    entity_name:        str = "NameMe"                  # Match name of entities dict key
    origin:             Point2D = field(default_factory=lambda: Point2D(0, 0))
    # pylint: disable=unnecessary-lambda
    amount_excited:     AmountExcited = field(default_factory=lambda: AmountExcited())
    size:               float = 0.2
    # points:             list[Point2D] = field(init=False)
    points:             list[Point2D] = field(default_factory=list)
    movement:           Movement = Movement()

    def set_initial_points(self) -> None:
        """Set the artwork vertices back to their non-wiggle values, plus any movement offset."""
        self.points = []
        # TODO: decouple line color from shape description?
        # I ignore this color anyway and assign it in self.draw()
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
        entity_name = self.entity_name
        if entity_name == "player":
            self.set_player_movement(ui_keys)
        else:
            self.movement.up = False
        if not timing.frame_counters["game"].is_paused:
            self.move()
            self.animate(timing)

    @property
    def is_moving(self) -> bool:
        """True if entity is moving."""
        return self.movement.is_moving

    def set_player_movement(self, ui_keys: UIKeys) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        movement.up = ui_keys.up_arrow
        movement.down = ui_keys.down_arrow
        movement.left = ui_keys.left_arrow
        movement.right = ui_keys.right_arrow

    def move(self) -> None:
        """Move the entity based on movement state"""
        movement = self.movement
        if self.entity_name == "player":
            origin = self.origin
            if movement.up:    origin.y += movement.speed
            if movement.down:  origin.y -= movement.speed
            if movement.right: origin.x += movement.speed
            if movement.left:  origin.x -= movement.speed
        # Update movement state
        movement.is_moving = (movement.up or movement.down or movement.left or movement.right)
        # If moving, update points
        if movement.is_moving:
            self.set_initial_points()

    def animate(self, timing: Timing) -> None:
        """Animate the entity.

        Animation speed is clocked by Timing.frame_counters['game'].clocked_events[event_name].
        """
        # Use counter for wiggling animation
        clocked_event = timing.frame_counters["game"].clocked_events[self.clocked_event_name]
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
                # TODO: instead of adjusting points here, adjust the amounts to offset each point.
                # Then we always apply those offsets in set_initial_points().
                point.x += random.uniform(-1*amount_excited, amount_excited)
                point.y += random.uniform(-1*amount_excited, amount_excited)

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        if self.entity_name == "player":
            color = Colors.line_player
        else:
            color = Colors.line_debug
        art.draw_lines(self.points, color)
