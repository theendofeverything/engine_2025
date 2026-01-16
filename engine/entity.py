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

from __future__ import annotations
from dataclasses import dataclass, field
import pathlib
import random
from enum import Enum, auto
from .geometry_types import Point2D, Vec2D
# from .drawing_shapes import Shape, Cross
from .drawing_shapes import Cross, Line2D
from .timing import Timing
from .colors import Colors
from .art import Art
from .ui import UIKeys
from .debug import Debug


FILE = pathlib.Path(__file__).name


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
    vec:    Vec2D = field(default_factory=lambda: Vec2D(x=0.0, y=0.0))
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
        # Adjust speed.vec.y based on forces up/down
        if is_going.up:
            movement.speed.vec.y += movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.y = min(movement.speed.vec.y, movement.speed.abs_max)
        if is_going.down:
            movement.speed.vec.y -= movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.y = max(movement.speed.vec.y, -1*movement.speed.abs_max)
        # If no force up/down, slide to a halt:
        if (not is_going.up) and (not is_going.down):
            if movement.speed.vec.y < 0:
                movement.speed.vec.y += movement.speed.slide
                # Speed approaches 0 from the left and stops at 0
                movement.speed.vec.y = min(movement.speed.vec.y, 0)
            elif movement.speed.vec.y > 0:
                movement.speed.vec.y -= movement.speed.slide
                # Speed approaches 0 from the right and stops at 0
                movement.speed.vec.y = max(movement.speed.vec.y, 0)
        # Adjust speed.vec.x based on forces right/left
        if is_going.right:
            movement.speed.vec.x += movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.x = min(movement.speed.vec.x, movement.speed.abs_max)
        if is_going.left:
            movement.speed.vec.x -= movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.x = max(movement.speed.vec.x, -1*movement.speed.abs_max)
        # If no force right/eft, slide to a halt:
        if (not is_going.right) and (not is_going.left):
            if movement.speed.vec.x < 0:
                movement.speed.vec.x += movement.speed.slide
                # Speed approaches 0 from the left and stops at 0
                movement.speed.vec.x = min(movement.speed.vec.x, 0)
            elif movement.speed.vec.x > 0:
                movement.speed.vec.x -= movement.speed.slide
                # Speed approaches 0 from the right and stops at 0
                movement.speed.vec.x = max(movement.speed.vec.x, 0)
        # if is_going.right:
        #     movement.speed.right += movement.speed.accel
        # else:
        #     movement.speed.right -= movement.speed.slide

        # if is_going.left:
        #     movement.speed.left += movement.speed.accel
        # else:
        #     movement.speed.left -= movement.speed.slide
        # Clamp speeds
        # movement.speed.right = min(movement.speed.right, movement.speed.abs_max)
        # movement.speed.right = max(movement.speed.right, 0)
        # movement.speed.left = min(movement.speed.left, movement.speed.abs_max)
        # movement.speed.left = max(movement.speed.left, 0)


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


class EntityType(Enum):
    """Categorize entities by type.

    >>> entity_type = EntityType.PLAYER
    >>> entity_type
    <EntityType.PLAYER: 1>
    >>> entity_type = EntityType.BACKGROUND_ART
    >>> entity_type
    <EntityType.BACKGROUND_ART: 2>
    >>> entity_type = EntityType.NPC
    >>> entity_type
    <EntityType.NPC: 3>
    """

    PLAYER = auto()
    BACKGROUND_ART = auto()
    NPC = auto()


# pylint: disable=too-many-instance-attributes
@dataclass
class Entity:
    """Any character in the game, such as the player.

    Tell entities apart based on the 'entity_name':
    - starts with "player": it is a player
    - starts with "bgnd" it is background art
    - starts with "enemy" it is an enemy

    TODO: change entity_name from string to enum

    API:
        is_moving():
            True if entity is moving.
        update(timing: Timing, ui_keys: UIKeys):
            If game is not paused, the entity animation updates (if the clocked_event period
            elapsed) and the entity moves (if keys are pressed).
        draw(art: Art):
            Connects lines between all points, including connecting last to first.

    >>> entities: dict[str, "Entity"] = {}
    >>> entity = Entity(debug=Debug(), entities=entities, entity_type=EntityType.BACKGROUND_ART,
    ... clocked_event_name = "period_3")
    >>> entity
    Entity(debug=Debug(hud=..., art=...), entities={},
        entity_type=<EntityType...>,
        entity_name='...',
        clocked_event_name='period_3',
        origin=Point2D(...),
        amount_excited=AmountExcited(...),
        size=...,
        artwork=Artwork(...),
        movement=Movement(...))
    """
    debug:              Debug
    entities:           dict[str, Entity]               # Give each entity access to all others
    entity_type:        EntityType
    entity_name:        str = "NameMe"                  # Match name of entities dict key
    clocked_event_name: str = "every_frame"             # Match name of clocked_events dict key
    # pylint: disable=unnecessary-lambda
    origin:             Point2D = field(default_factory=lambda: Point2D(0, 0))
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
        # Update points to get new position and remove old offsets before animating new offsets.
        self._reset_points()
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

    def player_update_from_ui(self, ui_keys: UIKeys) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        movement.is_going.up = ui_keys.up_arrow
        movement.is_going.down = ui_keys.down_arrow
        movement.is_going.left = ui_keys.left_arrow
        movement.is_going.right = ui_keys.right_arrow

    def npc_update(self) -> None:
        """Update movement state of NPC based on ?"""
        # Find the player entity. For now just look for key "player".
        if "player" in self.entities:
            player = self.entities["player"]
            aim = Vec2D.from_points(start=self.origin, end=player.origin)
            movement = self.movement
            #
            # TODO: write up a table of NPC speed values and resulting aim vectors to understand why
            # NPC keeps moving (it never considers itself locked in on the player).
            #
            # Floats: cannot compare against zero. Use epsilon to say "close enough".
            # 0.2/100 = 0.002
            # epsilon = self.size/100
            epsilon = 0
            if aim.x > epsilon:
                movement.is_going.right = True
                movement.is_going.left = False
            elif aim.x < -1*epsilon:
                movement.is_going.left = True
                movement.is_going.right = False
            else:
                movement.is_going.left = False
                movement.is_going.right = False
            debug = True

            def debug_npc_motion() -> None:
                self.debug.hud.print(f"+- Entity.npc_update() ({FILE})")
                self.debug.hud.print("|  +- Locals")
                self.debug.hud.print(f"|     +- aim = {aim.fmt(0.6)}")
                self.debug.hud.print(f"|     +- epsilon = size/100: {epsilon}")
                self.debug.hud.print("|  +- Movement Attrs")
                self.debug.hud.print(f"|     +- is_going.left: {movement.is_going.left}")
                self.debug.hud.print(f"|     +- is_going.right: {movement.is_going.right}")
                self.debug.hud.print(f"|     +- speed.accel: {movement.speed.accel}")
                self.debug.hud.print(f"|     +- speed.slide: {movement.speed.slide}")
                # LEFTOFF
                self.debug.hud.print(f"|     +- speed.vec: {movement.speed.vec.fmt(0.6)}")
            if debug:
                debug_npc_motion()
                self.debug.art.lines_gcs.append(
                        Line2D(
                            start=self.origin,
                            end=player.origin,
                            color=Colors.line_debug))

    def update(self, timing: Timing, ui_keys: UIKeys) -> None:
        """Update entity state based on the Timing -> Ticks and UI -> UIKeys."""
        entity_type = self.entity_type
        match entity_type:
            case EntityType.PLAYER:
                self.player_update_from_ui(ui_keys)
            case EntityType.NPC:
                self.npc_update()
            case _:
                pass
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
        origin = self.origin
        # Instead of modifying origin, modify speed.
        movement.update_speed()
        # Update position
        # origin.y += movement.speed.up - movement.speed.down
        origin.y += movement.speed.vec.y
        # origin.x += movement.speed.right - movement.speed.left
        origin.x += movement.speed.vec.x

        # Update movement state
        movement.is_moving = (is_going.up or is_going.down or is_going.left or is_going.right)

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        if self.entity_name == "player":
            color = Colors.line_player
        else:
            color = Colors.line_debug
        art.draw_lines(self.artwork.animated_points, color)
