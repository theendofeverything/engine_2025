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
from pygame import Color
from .geometry_types import Point2D, Vec2D, DirectedLineSeg2D
# from .drawing_shapes import Shape, Cross
from .drawing_shapes import Cross, Line2D
from .timing import Timing
from .colors import Colors
from .art import Art
from .debug import Debug


FILE = pathlib.Path(__file__).name


@dataclass
class AmountExcited:
    """How excited the entity animation is"""
    low: float = 0.005                                  # Low excitement
    high: float = 0.020                                 # High excitement


@dataclass
class PlayerForce:
    """Store True/False information on Player up/down/left/right."""
    up:     bool = False
    down:   bool = False
    left:   bool = False
    right:  bool = False


@dataclass
class Speed:
    """Store speed as a vector with a max value for any component.

    Temporary: "slide" models player's inertia
    """
    vec:    Vec2D = field(default_factory=lambda: Vec2D(x=0.0, y=0.0))
    slide:  float = 0.0015  # TODO: replace this with actual inertia
    abs_max: float = 0.02


@dataclass
class Force:
    """Force vector on the entity."""
    vec:    Vec2D = field(default_factory=lambda: Vec2D(x=0.0, y=0.0))


@dataclass
class Accel:
    """Acceleration vector of the entity."""
    vec:        Vec2D = field(default_factory=lambda: Vec2D(x=0.003, y=0.003))
    threshold:    float = 0.0015


# pylint: disable=too-many-instance-attributes
@dataclass
class Movement:
    """Entity movement data: speed and up/down/left/right, and whether or not it is moving."""
    # pylint: disable=unnecessary-lambda
    speed:      Speed = field(default_factory=lambda: Speed())
    force:      Force = field(default_factory=lambda: Force())
    accel:      Accel = field(default_factory=lambda: Accel())
    mass:       float = field(init=False)  # Entity sets mass based on size in __post_init__()
    player_force:   PlayerForce = field(default_factory=lambda: PlayerForce())
    is_excited:  bool = False
    follow_entity: str = ""  # Name of entity to follow
    dist_to_follow_entity: float = field(init=False)  # Entity sets goal distance based on size

    def update_npc_speed(self, abs_terminal_velocity: float) -> None:
        """Update speed of the NPC based on the forces calculated for this frame."""
        movement = self
        a = movement.accel.vec
        # Update velocity: v(n) = v(n-1) + a(n) (acceleration is force, for now)
        a.x = movement.force.vec.x/movement.mass
        a.y = movement.force.vec.y/movement.mass
        movement.speed.vec.x += a.x
        movement.speed.vec.y += a.y
        # Impose a terminal velocity on NPC based on player's maximum speed
        # (If player drags NPC left/right, NPC lags behind instead of overshooting)
        if movement.speed.vec.x > 0:
            movement.speed.vec.x = min(
                    movement.speed.vec.x,
                    abs_terminal_velocity)
        if movement.speed.vec.x < 0:
            movement.speed.vec.x = max(
                    movement.speed.vec.x,
                    -1*abs_terminal_velocity)
        if movement.speed.vec.y > 0:
            movement.speed.vec.y = min(
                    movement.speed.vec.y,
                    abs_terminal_velocity)
        if movement.speed.vec.y < 0:
            movement.speed.vec.y = max(
                    movement.speed.vec.y,
                    -1*abs_terminal_velocity)

    def update_player_speed(self) -> None:
        """Update player speed based on UI controls."""
        movement = self
        max_speed = movement.speed.abs_max
        # TODO: use player mass to get acceleration from force
        #       Then use player acceleration to get speed
        #       Instead of "slide" find a way to encode inertia.
        force = movement.force.vec
        movement.speed.vec.y += force.y
        movement.speed.vec.x += force.x
        # Clamp speed at max
        movement.speed.vec.y = max(min(movement.speed.vec.y, max_speed), -1*max_speed)
        movement.speed.vec.x = max(min(movement.speed.vec.x, max_speed), -1*max_speed)
        # If no force up/down, slide to a halt:
        if force.y == 0:
            if movement.speed.vec.y < 0:
                movement.speed.vec.y += movement.speed.slide
                # Speed approaches 0 from the left and stops at 0
                movement.speed.vec.y = min(movement.speed.vec.y, 0)
            elif movement.speed.vec.y > 0:
                movement.speed.vec.y -= movement.speed.slide
                # Speed approaches 0 from the right and stops at 0
                movement.speed.vec.y = max(movement.speed.vec.y, 0)
        # If no force right/left, slide to a halt:
        if force.x == 0:
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
    color:          Color = Colors.line

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

    Tell entities apart based on the 'entity_type': see EntityType.

    API:
        is_excited():
            True if entity is moving.
        update(timing: Timing):
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
    # amount_excited is proportional to size in __post_init__()
    amount_excited:     AmountExcited = field(default_factory=lambda: AmountExcited())
    size:               float = 0.2
    artwork:            Artwork = field(default_factory=lambda: Artwork())
    movement:           Movement = field(default_factory=lambda: Movement())

    def __post_init__(self) -> None:
        match self.entity_type:
            case EntityType.PLAYER:
                self.artwork.color = Colors.line_player
            case EntityType.NPC:
                self.artwork.color = Colors.line_debug
            case EntityType.BACKGROUND_ART:
                self.artwork.color = Colors.line
        self._reset_points()
        self._initialize_point_offsets()
        # Game can override these, but here are the defaults
        self.movement.mass = self.size * 5  # e.g., if size is 0.2, mass is 1
        self.amount_excited.high = self.size / 10
        self.amount_excited.low = self.size / 40
        self.movement.dist_to_follow_entity = self.size * 1

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

    # TODO: How do I want to control what entities look like? _reset_points() controls that now, but
    # it should just reset the points to their initial locations for the entity, whatever that is.
    # For now that can be determined by a shape. Where should I store the shape? I can just base it
    # for now on the entity_type. So that can stay in _reset_points() for now.
    def _reset_points(self) -> None:
        """Set the artwork vertices back to their non-wiggle values, plus any movement offset."""
        artwork = self.artwork
        artwork.points = []
        entity_type = self.entity_type
        # TODO: decouple line color from shape description?
        # I ignore this color anyway and assign it in self.draw()
        #
        match entity_type:
            case EntityType.PLAYER | EntityType.NPC:
                cross = Cross(
                        origin=self.origin,
                        size=self.size,
                        rotate45=True,
                        color=artwork.color)
                for line in cross.lines:
                    artwork.points.append(Point2D(line.start.x, line.start.y))
                    artwork.points.append(Point2D(line.end.x, line.end.y))
            case EntityType.BACKGROUND_ART:
                cross = Cross(
                        origin=self.origin,
                        size=self.size,
                        rotate45=False,
                        color=artwork.color)
                for line in cross.lines:
                    artwork.points.append(Point2D(line.start.x, line.start.y))
                    artwork.points.append(Point2D(line.end.x, line.end.y))

    def update(self, timing: Timing) -> None:
        """Update entity state based on the Timing -> Ticks and UI -> UIKeys.

        I update forces regardless of whether the game is paused. This is for two reasons:
            1) Forces do not accumulate, they are based on current state only. So the calculated
               will appear "paused" if the current state is paused.
            2) If I am debugging the force update code but skip the update because the game is
               paused, then my debug code does not show up in the HUD (I have snapshots for this,
               but then I need to clear the snapshot).
        """
        entity_type = self.entity_type
        movement = self.movement
        # Update the forces on the entity.
        match entity_type:
            case EntityType.PLAYER:
                # Player forces come from UI inputs
                self.update_player_forces_from_ui()
                if not timing.frame_counters["game"].is_paused:
                    movement.update_player_speed()
                    self.update_player_position()
            case EntityType.NPC:
                # NPC forces come from displacement to player and NPC speed
                follow_entity = self.movement.follow_entity
                it_exists = follow_entity in self.entities
                self.update_npc_forces(it_exists)
                my_max_speed = movement.speed.abs_max
                dragger_max_speed = self.entities[follow_entity].movement.speed.abs_max
                terminal_velocity = dragger_max_speed if it_exists else my_max_speed
                if not timing.frame_counters["game"].is_paused:
                    movement.update_npc_speed(abs_terminal_velocity=terminal_velocity)
                    self.update_npc_position()
            case _:
                pass
        # Update animation
        if not timing.frame_counters["game"].is_paused:
            self.animate(timing)

    def update_player_forces_from_ui(self) -> None:
        """Update movement state based on UI input from arrow keys."""
        movement = self.movement
        up = movement.player_force.up
        down = movement.player_force.down
        right = movement.player_force.right
        left = movement.player_force.left
        movement.is_excited = (up or down or left or right)
        # Rest the force vector to zero
        movement.force = Force()
        # Assign force (x,y) based on UI keys: -accel, 0, or accel
        force = movement.force.vec
        accel = movement.accel.vec
        mass = movement.mass
        if up:
            force.y += mass * accel.y
        if down:
            force.y -= mass * accel.y
        if right:
            force.x += mass * accel.x
        if left:
            force.x -= mass * accel.x

    # pylint: disable=too-many-locals
    def update_npc_forces(self, entity_i_follow_exists: bool) -> None:
        """Update forces on the NPC.

        NPC forces are based on:
            - previous velocity (friction)
            - previous displacement from player (spring)
        """
        debug = True
        if entity_i_follow_exists:
            movement = self.movement
            entity = self.entities[movement.follow_entity]
            # Calculate displacement vector (displacement of NPC from the entity)
            from_entity_to_me = DirectedLineSeg2D(start=entity.origin, end=self.origin)
            if debug:
                self.debug.art.lines_gcs.append(
                        Line2D(
                            start=from_entity_to_me.start,
                            end=from_entity_to_me.end,
                            color=Colors.line_debug))
            # start = entity.origin
            # end = self.origin
            # Set the goal location from the entity to follow
            closest = Vec2D.from_points(
                    start=from_entity_to_me.start,
                    end=from_entity_to_me.end
                    ).to_unit_vec()
            closest.scale_by(movement.dist_to_follow_entity)
            goal = Point2D(
                    x=entity.origin.x + closest.x,
                    y=entity.origin.y + closest.y
                    )

            # Displacement vector is from the goal to me
            d = Vec2D.from_points(start=goal, end=self.origin)
            # d = Vec2D.from_points(start=entity.origin, end=self.origin)
            # Get velocity vector
            movement = self.movement
            v = movement.speed.vec
            # Update forces
            # TODO: set up a better way to connect variables to user input from HUD
            controls = self.debug.hud.controls
            # fk(n) = -1*k*d(n-1)
            force_spring = Force(
                    vec=Vec2D(
                        x=-controls["k"]*d.x,
                        y=-controls["k"]*d.y))
            # fb(n) = -1*b*v(n-1)
            force_friction = Force(
                    vec=Vec2D(
                        x=-controls["b"]*v.x,
                        y=-controls["b"]*v.y))
            # ft(b) = fk(n) + fb(n)
            movement.force.vec.x = force_spring.vec.x + force_friction.vec.x
            movement.force.vec.y = force_spring.vec.y + force_friction.vec.y

            # Update excited state:
            # Look excited if you feel forces acting on you
            # force_feel = movement.mass * movement.accel.abs_max/2  # Threshold for feeling force
            force_feel = movement.mass * movement.accel.threshold  # Threshold for feeling force
            force = movement.force.vec
            movement.is_excited = (
                    (force.x > force_feel) or (force.y > force_feel)
                    ) or (
                    (force.x < -force_feel) or (force.y < -force_feel))

            if debug:
                hud = self.debug.hud

                def debug_npc_forces() -> None:
                    hud.print("|")
                    hud.print(f"+- {self.entity_name}.update.update_npc_forces() ({FILE})")
                    hud.print("|  +- Movement Attrs")
                    hud.print(f"|     +- follow_entity: {movement.follow_entity}")
                    follow_speed = entity.movement.speed.vec
                    follow_accel = entity.movement.accel.vec
                    hud.print(f"|     +- follow_entity speed: {follow_speed.fmt(0.6)}")
                    hud.print(f"|     +- follow_entity accel: {follow_accel.fmt(0.6)}")
                    hud.print(f"|     +- speed.vec: {movement.speed.vec.fmt(0.6)}")
                    hud.print(f"|     +- force.vec: {movement.force.vec.fmt(0.6)}")
                    hud.print(f"|     +- mass: {movement.mass}")
                    hud.print("|  +- Locals")
                    hud.print(f"|     +- k:float = {controls['k']}")
                    hud.print(f"|     +- b:float = {controls['b']}")
                    start = from_entity_to_me.start
                    end = from_entity_to_me.end
                    hud.print(f"|     +- d:Vec2D = {d.fmt(0.6)}: {start} to {end}")
                    hud.print(f"|     +- v:Vec2D = {v.fmt(0.6)}")
                debug_npc_forces()

    @property
    def is_excited(self) -> bool:
        """True if entity is moving."""
        return self.movement.is_excited

    def update_npc_position(self) -> None:
        """Update position of NPC"""
        # Update displacement: d(n) = d(n-1) + v(n)
        movement = self.movement
        self.origin.x += movement.speed.vec.x
        self.origin.y += movement.speed.vec.y

    def update_player_position(self) -> None:
        """Update player position"""
        movement = self.movement
        origin = self.origin
        origin.y += movement.speed.vec.y
        origin.x += movement.speed.vec.x

    def draw(self, art: Art) -> None:
        """Draw entity in the GCS. Game must call update() before draw()."""
        artwork = self.artwork
        art.draw_lines(artwork.animated_points, artwork.color)
