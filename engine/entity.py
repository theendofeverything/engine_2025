"""Entities are things like the Player that track their own state.

TODO: Separate my "player" and "cross" entities (they overlap right now)
TODO: How do I want to set up entity artwork?
- Make methods like "from_cross", "from_lines", "from_points" to provide different ways of making
  entity art.
- [x] Start with making a character that is a wiggling cross.
- [ ] Then try a wiggling triangle.

Entity Documentation (WIP)
--------------------------
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
    low: float = 0.005                                  # Low excitement
    high: float = 0.020                                 # High excitement


@dataclass
class IsGoing:
    """Store True/False information on up/down/left/right."""
    up:     bool = False
    down:   bool = False
    left:   bool = False
    right:  bool = False


@dataclass
class Speed:
    """Store speed information on up/down/left/right."""
    up:     float = 0.0
    down:   float = 0.0
    left:   float = 0.0
    right:  float = 0.0
    accel:  float = 0.003
    slide:  float = 0.0015
    abs_max: float = 0.02


@dataclass
class Movement:
    """Entity movement data: speed and up/down/left/right, and whether or not it is moving."""
    # pylint: disable=unnecessary-lambda
    speed:      Speed = field(default_factory=lambda: Speed())
    is_going:   IsGoing = field(default_factory=lambda: IsGoing())
    is_moving:  bool = False

    def update_speed(self) -> None:
        """Update speed. Used in Entity.move()."""
        movement = self
        is_going = movement.is_going
        # To update speed: increase if controller is going that way, decrease if not.
        # TODO: update based on elapsed time, not number of frames.
        # TODO: refactor speed update to avoid repetition (every direction has the same thing done
        # to it).
        if is_going.up:
            movement.speed.up += movement.speed.accel
        else:
            movement.speed.up -= movement.speed.slide

        if is_going.down:
            movement.speed.down += movement.speed.accel
        else:
            movement.speed.down -= movement.speed.slide

        if is_going.right:
            movement.speed.right += movement.speed.accel
        else:
            movement.speed.right -= movement.speed.slide

        if is_going.left:
            movement.speed.left += movement.speed.accel
        else:
            movement.speed.left -= movement.speed.slide
        # Clamp speeds
        movement.speed.up = min(movement.speed.up, movement.speed.abs_max)
        movement.speed.up = max(movement.speed.up, 0)
        movement.speed.down = min(movement.speed.down, movement.speed.abs_max)
        movement.speed.down = max(movement.speed.down, 0)
        movement.speed.right = min(movement.speed.right, movement.speed.abs_max)
        movement.speed.right = max(movement.speed.right, 0)
        movement.speed.left = min(movement.speed.left, movement.speed.abs_max)
        movement.speed.left = max(movement.speed.left, 0)


# Next: use shape: Shape
@dataclass
class Artwork:
    """Entity points and the offsets to each point that are used in animation."""
    # shape:          Shape
    points:         list[Point2D] = field(default_factory=list)
    point_offsets:  list[Vec2D] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.points = []
        self.point_offsets = []

    @property
    def animated_points(self) -> list[Point2D]:
        """Animate points by adding point offsets to artwork points."""
        points: list[Point2D] = []
        for point, offset in zip(self.points, self.point_offsets):
            points.append(Point2D(point.x + offset.x, point.y + offset.y))
        return points


@dataclass
class Entity:
    """Any character in the game, such as the player.

    Tell entities apart based on the 'entity_name':
    - starts with "player": it is a player
    - starts with "bgnd" it is background art
    - starts with "enemy" it is an enemy

    API:
        is_moving():
            True if entity is moving.
        update(timing: Timing, ui_keys: UIKeys):
            If game is not paused, the entity animation updates (if the clocked_event period
            elapsed) and the entity moves (if keys are pressed).
        draw(art: Art):
            Connects lines between all points, including connecting last to first.

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

    def set_player_movement(self, ui_keys: UIKeys) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        movement.is_going.up = ui_keys.up_arrow
        movement.is_going.down = ui_keys.down_arrow
        movement.is_going.left = ui_keys.left_arrow
        movement.is_going.right = ui_keys.right_arrow

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
            self.movement.is_going.up = False
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
        is_going = movement.is_going
        if self.entity_name == "player":
            origin = self.origin
            # Instead of modifying origin, modify speed.
            movement.update_speed()
            # Update position
            origin.y += movement.speed.up - movement.speed.down
            origin.x += movement.speed.right - movement.speed.left
        # Update movement state
        movement.is_moving = (is_going.up or is_going.down or is_going.left or is_going.right)
        # If moving, update points
        self._reset_points()
        # if movement.is_moving:

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        if self.entity_name == "player":
            color = Colors.line_player
        else:
            color = Colors.line_debug
        art.draw_lines(self.artwork.animated_points, color)
