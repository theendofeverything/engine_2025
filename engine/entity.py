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
from .geometry_types import Point2D, Vec2D
# from .drawing_shapes import Shape, Cross
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


# Next: use point_offsets, then start using shape: Shape
@dataclass
class Artwork:
    """Entity points and the offsets to each point that are used in animation."""
    # shape:          Shape
    points:         list[Point2D] = field(default_factory=list)
    point_offsets:  list[Vec2D] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.points = []
        self.point_offsets = []


# Create "Player" by checking entity name.
# TODO: Instead, try creating a new class for Player that uses Entity by composition.
@dataclass
class Entity:
    """Any character in the game, such as the player.

    API:
        is_moving():
            True if entity is moving.
        update(timing: Timing, ui_keys: UIKeys):
            If game is not paused, the entity animation updates (if the clocked_event period
            elapsed) and the entity moves (if keys are pressed).
        draw(art: Art):
            Connects lines between all points, including connecting last to first.

    The entity has a basic shape, defined in Art.
    The shape is made of points. For now, we render the entity by connecting all points with lines.

    To give Entities a bit of life, we move those points a bit each frame (by default we move those
    points every frame, but we can also choose to wait a whole number of frames by selecting one of
    ClockedEvents from the Timing FrameCounters.).

    So animations are done by adding a small random wiggle to each point.
    The amount to move each point is stored in an array of point_offsets.
    The animation is clocked by a clocked_event
    (the period of the animation is some whole number of game frame periods).

    TODO: finish drawing this
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
        entity_name='...',
        origin=Point2D(...),
        amount_excited=AmountExcited(...),
        size=...,
        artwork=Artwork(...),
        movement=Movement(...))
    """
    clocked_event_name: str = "every_frame"             # Match name of clocked_events dict key
    entity_name:        str = "NameMe"                  # Match name of entities dict key
    origin:             Point2D = field(default_factory=lambda: Point2D(0, 0))
    # pylint: disable=unnecessary-lambda
    amount_excited:     AmountExcited = field(default_factory=lambda: AmountExcited())
    size:               float = 0.2
    artwork:            Artwork = field(default_factory=lambda: Artwork())
    movement:           Movement = field(default_factory=lambda: Movement())

    def __post_init__(self) -> None:
        self._reset_points()
        self._initialize_point_offsets()

    def _initialize_point_offsets(self) -> None:
        for _ in self.artwork.points:
            self.artwork.point_offsets.append(Vec2D(0, 0))

    def animate(self, timing: Timing) -> None:
        """Animate the entity.

        Animation speed is clocked by Timing.frame_counters['game'].clocked_events[event_name].
        """
        # Use counter for wiggling animation
        clocked_event = timing.frame_counters["game"].clocked_events[self.clocked_event_name]
        if clocked_event.is_period:
            # self._reset_points()
            if self.is_moving:
                amount_excited = self.amount_excited.high
            else:
                amount_excited = self.amount_excited.low
            for offset in self.artwork.point_offsets:
                offset.x = random.uniform(-1*amount_excited, amount_excited)
                offset.y = random.uniform(-1*amount_excited, amount_excited)
            # for point in self.artwork.points:
            #     # TODO: instead of adjusting points here, adjust the amounts to offset each point.
            #     # Then we always apply those offsets in _reset_points().
            #     point.x += random.uniform(-1*amount_excited, amount_excited)
            #     point.y += random.uniform(-1*amount_excited, amount_excited)

    @property
    def points(self) -> list[Point2D]:
        """Artwork points offset by their animation offsets."""
        points: list[Point2D] = []
        for point, offset in zip(self.artwork.points, self.artwork.point_offsets):
            points.append(Point2D(point.x + offset.x, point.y + offset.y))
        return points

    # TODO: pull this out to a Player class
    def set_player_movement(self, ui_keys: UIKeys) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        movement.up = ui_keys.up_arrow
        movement.down = ui_keys.down_arrow
        movement.left = ui_keys.left_arrow
        movement.right = ui_keys.right_arrow

    def _reset_points(self) -> None:
        """Set the artwork vertices back to their non-wiggle values, plus any movement offset."""
        self.artwork.points = []
        # TODO: decouple line color from shape description?
        # I ignore this color anyway and assign it in self.draw()
        cross = Cross(
                origin=self.origin,
                size=self.size,
                rotate45=True,
                color=Colors.line)
        for line in cross.lines:
            self.artwork.points.append(Point2D(line.start.x, line.start.y))
            self.artwork.points.append(Point2D(line.end.x, line.end.y))

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
            self._reset_points()

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        if self.entity_name == "player":
            color = Colors.line_player
        else:
            color = Colors.line_debug
        art.draw_lines(self.points, color)
