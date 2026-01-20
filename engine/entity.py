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
    accel_abs_max:  float = 0.003
    slide:  float = 0.0015
    abs_max: float = 0.02


@dataclass
class Force:
    """Force vector on the entity."""
    vec:    Vec2D = field(default_factory=lambda: Vec2D(x=0.0, y=0.0))


@dataclass
class Movement:
    """Entity movement data: speed and up/down/left/right, and whether or not it is moving."""
    # pylint: disable=unnecessary-lambda
    speed:      Speed = field(default_factory=lambda: Speed())
    force:      Force = field(default_factory=lambda: Force())
    is_force:   IsGoing = field(default_factory=lambda: IsGoing())
    is_excited:  bool = False

    def update_npc_speed(self) -> None:
        """Update speed of the NPC based on the forces calculated for this frame."""
        self.speed.vec.x += self.force.vec.x
        self.speed.vec.y += self.force.vec.y

    def update_speed(self) -> None:
        """Update speed. Used in Entity.move()."""
        movement = self
        is_force = movement.is_force
        # To update speed:
        #   Increase by speed.accel if a force (controller or aim) is going that way.
        #   Decrease by speed.slide if no force in that x or y component.
        # TODO: update based on elapsed time, not number of frames.
        # TODO: refactor speed update to avoid repetition (x and y do the same things).
        # Adjust speed.vec.y based on forces up/down
        if is_force.up:
            movement.speed.vec.y += movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.y = min(movement.speed.vec.y, movement.speed.abs_max)
        if is_force.down:
            movement.speed.vec.y -= movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.y = max(movement.speed.vec.y, -1*movement.speed.abs_max)
        # Adjust speed.vec.x based on forces right/left
        if is_force.right:
            movement.speed.vec.x += movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.x = min(movement.speed.vec.x, movement.speed.abs_max)
        if is_force.left:
            movement.speed.vec.x -= movement.speed.accel
            # Clamp speed at max
            movement.speed.vec.x = max(movement.speed.vec.x, -1*movement.speed.abs_max)
        # If no force up/down, slide to a halt:
        if (not is_force.up) and (not is_force.down):
            if movement.speed.vec.y < 0:
                movement.speed.vec.y += movement.speed.slide
                # Speed approaches 0 from the left and stops at 0
                movement.speed.vec.y = min(movement.speed.vec.y, 0)
            elif movement.speed.vec.y > 0:
                movement.speed.vec.y -= movement.speed.slide
                # Speed approaches 0 from the right and stops at 0
                movement.speed.vec.y = max(movement.speed.vec.y, 0)
        # If no force right/left, slide to a halt:
        if (not is_force.right) and (not is_force.left):
            if movement.speed.vec.x < 0:
                movement.speed.vec.x += movement.speed.slide
                # Speed approaches 0 from the left and stops at 0
                movement.speed.vec.x = min(movement.speed.vec.x, 0)
            elif movement.speed.vec.x > 0:
                movement.speed.vec.x -= movement.speed.slide
                # Speed approaches 0 from the right and stops at 0
                movement.speed.vec.x = max(movement.speed.vec.x, 0)


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
        is_excited():
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
            if self.is_excited:
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

    def player_update_forces_from_ui(self, ui_keys: UIKeys) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        movement.is_force.up = ui_keys.up_arrow
        movement.is_force.down = ui_keys.down_arrow
        movement.is_force.left = ui_keys.left_arrow
        movement.is_force.right = ui_keys.right_arrow

    def update_npc_forces(self) -> None:
        """Update forces on the NPC based on previous displacement and velocity.
        """

    def npc_update_forces_old(self) -> None:
        """Update forces on NPC"""
        # Find the player entity. For now just look for key "player".
        if "player" in self.entities:
            player = self.entities["player"]
            aim = Vec2D.from_points(start=self.origin, end=player.origin)
            movement = self.movement
            # This is garbage.
            # Floats: cannot compare against zero. Use epsilon to say "close enough".
            # 0.2/100 = 0.002
            # epsilon = self.size/100
            # epsilon = 10*self.movement.speed.accel
            epsilon = 0
            if aim.x > epsilon:
                movement.speed.accel = movement.speed.accel_abs_max
                movement.is_force.right = True
                movement.is_force.left = False
            elif aim.x < -1*epsilon:
                movement.speed.accel = movement.speed.accel_abs_max
                movement.is_force.left = True
                movement.is_force.right = False
            else:
                # self.movement.speed.accel = self.movement.speed.accel/3
                movement.is_force.left = False
                movement.is_force.right = False

            debug = True

            def debug_npc_motion() -> None:
                self.debug.hud.print(f"+- Entity.npc_update_forces_old() ({FILE})")
                self.debug.hud.print("|  +- Locals")
                self.debug.hud.print(f"|     +- aim = {aim.fmt(0.6)}")
                # self.debug.hud.print(f"|     +- epsilon = size/100: {epsilon}")
                self.debug.hud.print("|  +- Movement Attrs")
                self.debug.hud.print(f"|     +- is_force.left: {movement.is_force.left}")
                self.debug.hud.print(f"|     +- is_force.right: {movement.is_force.right}")
                self.debug.hud.print(f"|     +- speed.accel: {movement.speed.accel}")
                self.debug.hud.print(f"|     +- speed.slide: {movement.speed.slide}")
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
        # Update the forces on the entity.
        match entity_type:
            case EntityType.PLAYER:
                # Player forces come from UI inputs
                self.player_update_forces_from_ui(ui_keys)
                if not timing.frame_counters["game"].is_paused:
                    self.move()     # Move player/NPR according to forces
                    self.animate(timing)
            case EntityType.NPC:
                # NPC forces are calculated from previous values of displacement and velocity
                # TODO: forces should NOT update if game is paused (should it matter? Bug is here)
                # self.update_npc_forces()  # Set NPC forces
                if "player" in self.entities:
                    player = self.entities["player"]
                    debug = True
                    if debug:
                        self.debug.art.lines_gcs.append(
                                Line2D(
                                    start=self.origin,
                                    end=player.origin,
                                    color=Colors.line_debug))

                    # Calculate displacement vector (displacement of NPC from the player)
                    start = player.origin
                    end = self.origin
                    d = Vec2D.from_points(start=start, end=end)
                    # Get velocity vector
                    movement = self.movement
                    v = movement.speed.vec
                    # Update forces
                    # TODO: set up a better way to connect variables to user input from HUD
                    # k = 0.0003                                   # Spring constant
                    # b = 0.015                                  # Damping constant
                    k = self.debug.hud.controls["k"]
                    b = self.debug.hud.controls["b"]
                    # fk(n) = -1*k*d(n-1)
                    force_spring = Force(vec=Vec2D(-k*d.x, 0))
                    # fb(n) = -1*b*v(n-1)
                    force_friction = Force(vec=Vec2D(-b*v.x, 0))
                    # ft(b) = fk(n) + fb(n)
                    movement.force.vec.x = force_spring.vec.x + force_friction.vec.x

                    # Update velocity: v(n) = v(n-1) + a(n)
                    movement.speed.vec.x += movement.force.vec.x
                    # Impose a terminal velocity on NPC based on player's maximum speed
                    # (If player drags NPC left/right, NPC lags behind instead of overshooting)
                    if movement.speed.vec.x > 0:
                        movement.speed.vec.x = min(
                                movement.speed.vec.x,
                                player.movement.speed.abs_max)
                    if movement.speed.vec.x < 0:
                        movement.speed.vec.x = max(
                                movement.speed.vec.x,
                                -1*player.movement.speed.abs_max)
                    # Update displacement: d(n) = d(n-1) + v(n)
                    self.origin.x += movement.speed.vec.x
                    # Update excited state
                    force_feel = movement.speed.accel_abs_max/2
                    force_x = movement.force.vec.x
                    force_y = movement.force.vec.y
                    movement.is_excited = (force_x > force_feel) or (force_y > force_feel)
                    self.animate(timing)

                    if debug:
                        hud = self.debug.hud

                        def debug_npc_motion() -> None:
                            hud.print(f"+- Entity.update() ({FILE})")
                            hud.print("|  +- Locals")
                            hud.print(f"|     +- k:float = {k}")
                            hud.print(f"|     +- b:float = {b}")
                            hud.print(f"|     +- d:Vec2D = {d.fmt(0.6)}: {start} to {end}")
                            hud.print(f"|     +- v:Vec2D = {v.fmt(0.6)}")
                            hud.print("|  +- Movement Attrs")
                            hud.print(f"|     +- speed.vec: {movement.speed.vec.fmt(0.6)}")
                            hud.print(f"|     +- force.vec: {movement.force.vec.fmt(0.6)}")
                            player_speed = player.movement.speed.vec
                            player_accel = player.movement.speed.accel
                            hud.print(f"|     +- player speed: {player_speed}")
                            hud.print(f"|     +- player accel: {player_accel}")
                        debug_npc_motion()

            case _:
                pass

    @property
    def is_excited(self) -> bool:
        """True if entity is moving."""
        return self.movement.is_excited

    def move(self) -> None:
        """Move the entity based on movement state"""
        movement = self.movement
        is_force = movement.is_force
        origin = self.origin
        # Instead of modifying origin, modify speed.
        entity_type = self.entity_type
        match entity_type:
            case EntityType.PLAYER:
                movement.update_speed()
            case EntityType.NPC:
                movement.update_npc_speed()
                # movement.update_speed()
            case _:
                pass
        # Update position
        # origin.y += movement.speed.up - movement.speed.down
        origin.y += movement.speed.vec.y
        # origin.x += movement.speed.right - movement.speed.left
        origin.x += movement.speed.vec.x

        # Update excited state
        movement.is_excited = (is_force.up or is_force.down or is_force.left or is_force.right)

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        if self.entity_name == "player":
            color = Colors.line_player
        else:
            color = Colors.line_debug
        art.draw_lines(self.artwork.animated_points, color)
