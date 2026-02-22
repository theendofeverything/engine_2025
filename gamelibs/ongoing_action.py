"""OngoingAction is a helper struct to organize Game.

OngoingAction tracks panning and similar mouse actions:
    - mouse panning state -- see OngoingAction.panning
    - click-drag player teleport -- OngoingAction.drag_player_is_active

Tracking state is necessary for these sustained actions. Just handling events is insufficient. For
example, while Shift + left-mouse-button are held, drag the player around the screen. We can detect
when Shift is pressed and released and when the left-mouse-button is pressed and released. But we
need to track those states to know that the action is ongoing in the game loop iterations after the
press and before the release.

Usage:
    from gamelibs.ongoing_action import OngoingAction

    @dataclass
    class Game:
        ...
        ongoing_action: OngoingAction = OngoingAction()
        ...
        def loop(self, log: logging.Logger) -> None:
            ...
            self.ui.consume_event_queue(log)  # Iterate over all user events
            self.ongoing_action.update(self)
"""
from dataclasses import dataclass, field
import pygame
from engine.geometry_types import Point2D, Vec2D, DirectedLineSeg2D


@dataclass
class Panning:
    """Track mouse panning state.

    Attributes:
        is_active (bool):
            Panning is in two states: either active (is_active=True) or inactive
            (is_active=False).
        begin (Point2D):
            Position in the pixel coordinate system when panning transitioned to
            the active state. While in the active state, 'begin' does not
            change.
        end (Point2D):
            Latest mouse position in the pixel coordinate system while panning:
            the game loads 'end' with the mouse position on every iteration of
            the game loop.
        vector (Vec2D):
            Amount of mouse pan, obtained from end - begin.
            The 'panning.vector' is picked up during rendering, as follows:
                When the game loop renders drawing entities, it converts entity
                coordinates from GCS to PCS:
                    coord_sys.xfm(v:Vec2D, coord_sys.matrix.gcs_to_pcs)

                That coordinate transform matrix is calculated using the origin
                offset vector:
                    coord_sys.translation

                And coord_sys.translation is calculated using the
                'panning.vector' (this attribute).

    >>> panning = Panning()                             # Track panning state
    >>> mouse_pos = (123, 456)                          # Position when button 1 was pressed
    >>> panning.begin = Point2D.from_tuple(mouse_pos)   # Track panning begin position
    >>> mouse_pos = (246, 456)                          # Position later while still panning
    >>> panning.end = Point2D.from_tuple(mouse_pos)     # Track latest panning position
    >>> panning.vector                                  # Report the latest panning vector
    Vec2D(x=123, y=0)
    """
    begin:                  Point2D = field(init=False)
    end:                    Point2D = Point2D(0, 0)     # Dummy initial value
    is_active:              bool = False

    def __post_init__(self) -> None:
        self.begin = self.end                           # Zero-out the panning vector

    @property
    def vector(self) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=self.begin, end=self.end)

    def start(self, position: tuple[int | float, int | float]) -> None:
        """User started panning."""
        panning = self
        panning.is_active = True
        panning.begin = Point2D.from_tuple(position)

    def stop(self, game: "Game") -> None:
        """User stopped panning."""
        panning = self
        panning.is_active = False
        game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
        panning.begin = panning.end  # Zero-out the panning vector

    def update(self) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game
        view on the screen:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- panning.vector

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.begin
        """
        panning = self
        if panning.is_active:
            mouse_pos = pygame.mouse.get_pos()
            panning.end = Point2D.from_tuple(mouse_pos)


class OngoingAction:
    """Actions that last for multiple frames such as click-drag.

    - Panning is a Ctrl+Click-Drag
    - Teleport (or pulling on the player) is a Shift+Click-Drag

    The key modifiers and specific mouse buttons might change. But these will always be a
    click-drag. It is simpler to just query the mouse position here than to use the mouse motion
    events.
    """

    panning: Panning = Panning()
    drag_player_is_active: bool = False

    def update(self, game: "Game") -> None:
        """Update all ongoing actions."""
        ongoing_action = self
        ongoing_action.panning.update()
        ongoing_action.drag_player(game)

    @staticmethod
    def drag_player(game: "Game") -> None:
        """Teleport player to mouse, like pulling on player and NPCs."""
        if game.input_mapper.ongoing_action.drag_player_is_active:
            # Get mouse position in game coordinates
            mouse_p = Point2D.from_tuple(pygame.mouse.get_pos())
            mouse_g = game.coord_sys.xfm(
                    mouse_p.as_vec(),
                    game.coord_sys.matrix.pcs_to_gcs
                    ).as_point()
            player_to_mouse = DirectedLineSeg2D(
                    start=game.entities["player"].origin,
                    end=mouse_g)
            # Teleport NPC2 to mouse
            game.entities["cross2"].origin = player_to_mouse.parametric_point(1.0)
            # Teleport NPC1 to half-way between player and NPC2
            game.entities["cross1"].origin = player_to_mouse.parametric_point(0.5)
