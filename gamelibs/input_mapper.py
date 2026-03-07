# flake8: noqa: E501
"""Map inputs to actions.

Note that pygame has two different codes for modifier keys depending on usage. For example:
    pygame.K_RSHIFT -- Code to check if the Right-Shift key is having its own KEYDOWN or KEYUP event
    pygame.KMOD_RSHIFT -- Code to check if Right-Shift is modifying another event
"""

from __future__ import annotations
from enum import Enum, IntEnum, auto
import sys
import logging
import pygame
from engine.geometry_types import Point2D, Vec2D, DirectedLineSeg2D

log = logging.getLogger(__name__)


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
            The 'Panning.vector()' is picked up during rendering, as follows:
                When the game loop renders drawing entities, it converts entity
                coordinates from GCS to PCS:
                    coord_sys.xfm(v:Vec2D, coord_sys.matrix.gcs_to_pcs)

                That coordinate transform matrix is calculated using the origin
                offset vector:
                    coord_sys.translation

                And coord_sys.translation is calculated using the
                'Panning.vector()' (this attribute).

    >>> mouse_pos = (123, 456)                          # Position when button 1 was pressed
    >>> Panning.begin = Point2D.from_tuple(mouse_pos)   # Track panning begin position
    >>> mouse_pos = (246, 456)                          # Position later while still panning
    >>> Panning.end = Point2D.from_tuple(mouse_pos)     # Track latest panning position
    >>> Panning.vector()                                # Report the latest panning vector
    Vec2D(x=123, y=0)
    """
    begin:                  Point2D = Point2D(0, 0)     # Dummy initial value
    end:                    Point2D = Point2D(0, 0)     # Zero-out the panning vector
    is_active:              bool = False

    @classmethod
    def vector(cls) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=cls.begin, end=cls.end)

    @classmethod
    def start(cls, position: tuple[int | float, int | float]) -> None:
        """User started panning."""
        panning = cls
        panning.is_active = True
        panning.begin = Point2D.from_tuple(position)

    @classmethod
    def stop(cls, game: "Game") -> None:
        """User stopped panning."""
        panning = cls
        panning.is_active = False
        game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
        panning.begin = panning.end  # Zero-out the panning vector

    @classmethod
    def update(cls) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game
        view on the screen:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- Panning.vector()

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - Panning.vector() = Panning.end - Panning.begin
        """
        panning = cls
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

    Details
    OngoingAction is a helper struct to organize Game.

    OngoingAction tracks panning and similar mouse actions:
        - mouse panning state -- see Panning
        - click-drag player teleport -- OngoingAction.drag_player_is_active

    Tracking state is necessary for these sustained actions. Just handling events is insufficient.
    For example, while Shift + left-mouse-button are held, drag the player around the screen. We can
    detect when Shift is pressed and released and when the left-mouse-button is pressed and
    released. But we need to track those states to know that the action is ongoing in the game loop
    iterations after the press and before the release.

    Usage:
        from gamelibs.ongoing_action import OngoingAction

        @dataclass
        class Game:
            ...
            ongoing_action: OngoingAction = OngoingAction()
            ...
            def loop(self) -> None:
                ...
                self.ui.consume_event_queue()  # Iterate over all user events
                self.ongoing_action.update(self)
    """

    drag_player_is_active: bool = False

    def update(self, game: "Game") -> None:
        """Update all ongoing actions."""
        ongoing_action = self
        Panning.update()
        ongoing_action.drag_player(game)

    @staticmethod
    def drag_player(game: "Game") -> None:
        """Teleport player to mouse, like pulling on player and NPCs."""
        # if game.input_mapper.ongoing_action.drag_player_is_active:
        if InputMapper.ongoing_action.drag_player_is_active:
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


class Action(Enum):
    """Enumerate all actions for the InputMapper."""
    QUIT = auto()
    CLEAR_DEBUG_SNAPSHOT_ARTWORK = auto()
    TOGGLE_DEBUG_ART_OVERLAY = auto()
    TOGGLE_FULLSCREEN = auto()
    TOGGLE_DEBUG_HUD = auto()
    TOGGLE_PAUSE = auto()
    FONT_SIZE_INCREASE = auto()
    FONT_SIZE_DECREASE = auto()
    CONTROLS_ADJUST_K_LESS = auto()
    CONTROLS_ADJUST_K_MORE = auto()
    CONTROLS_ADJUST_B_LESS = auto()
    CONTROLS_ADJUST_B_MORE = auto()
    CONTROLS_PICK_MODE_1 = auto()
    CONTROLS_PICK_MODE_2 = auto()
    CONTROLS_PICK_MODE_3 = auto()
    PLAYER_MOVE_LEFT_GO = auto()
    PLAYER_MOVE_RIGHT_GO = auto()
    PLAYER_MOVE_UP_GO = auto()
    PLAYER_MOVE_DOWN_GO = auto()
    PLAYER_MOVE_LEFT_STOP = auto()
    PLAYER_MOVE_RIGHT_STOP = auto()
    PLAYER_MOVE_UP_STOP = auto()
    PLAYER_MOVE_DOWN_STOP = auto()
    START_PANNING = auto()
    STOP_PANNING = auto()
    START_DRAG_PLAYER = auto()
    STOP_DRAG_PLAYER = auto()


class MouseButton(IntEnum):
    """Enumerate the mouse button values from pygame.Event.button.

    >>> MouseButton.LEFT
    <MouseButton.LEFT: 1>
    """
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5

    @classmethod
    def from_event(cls, event: pygame.Event) -> MouseButton:
        """Get MouseButton from an event (uses event.button)."""
        return cls(event.button)


class Mouse:
    """Track mouse state in a Global Singleton.

    Button state begins with no buttons pressed:
    >>> Mouse.is_pressed(MouseButton.LEFT)
    False

    Simulate a left-click:
    >>> event = pygame.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})

    Update the button state:
    >>> Mouse.update(event)

    Check that we have updated the state of the left mouse button:
    >>> Mouse.is_pressed(MouseButton.LEFT)
    True

    Convert pygame.Event.button 'int' type to a MouseButton Enum:
    >>> mouse_button = MouseButton.from_event(event)

    Print the button state (TRUE) using its name (LEFT) instead of its value (1):
    >>> print(f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
    Mouse.is_pressed(LEFT): True

    Note the use of 'MouseButton' vs 'MouseButton.name':
        - 'MouseButton' gets the 'int' value (1, 2, etc.)
        - 'MouseButton.name' gets the button name ('LEFT', 'MIDDLE', etc.)
    """
    # Store states for all 5 buttons: Pressed (True) and NotPressed (False)
    _state = {button.value: False for button in MouseButton}

    @classmethod
    def update(cls, event: pygame.Event) -> None:
        """Update the state of all buttons in MouseButton."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                cls._state[event.button] = True
            case pygame.MOUSEBUTTONUP:
                cls._state[event.button] = False

    @classmethod
    def is_pressed(cls, button: MouseButton) -> bool:
        """Return True/False if button MouseButton is pressed.

        If the "button" does not exist, return False instead of None:
        >>> Mouse.is_pressed(6)
        False
        """
        return cls._state.get(button, False)


class ButtonDirection(Enum):
    """Enumerate names for MOUSEBUTTONUP and MOUSEBUTTONDOWN."""
    UP = auto()
    DOWN = auto()


class KeyDirection(Enum):
    """Enumerate names for KEYUP and KEYDOWN instead of just using bool."""
    UP = auto()
    DOWN = auto()


class KeyModifier(Enum):
    """Assign key modifiers to more general names or to specific actions.

    An example of mapping to a more general name is:
        NO_MODIFIER = pygame.KMOD_NONE

    An example of mapping to a specific action is
        PANNING = pygame.KMOD_CTRL
    """
    NO_MODIFIER         = pygame.KMOD_NONE
    SHIFT               = pygame.KMOD_SHIFT
    CTRL                = pygame.KMOD_CTRL
    SHIFT_CTRL          = pygame.KMOD_SHIFT | pygame.KMOD_CTRL
    PANNING             = pygame.KMOD_CTRL

    @classmethod
    def from_kmod(cls, kmod: int) -> KeyModifier:
        """Get a KeyModifier from the pygame kmod value returned by UI.kmod_simplify(kmod)."""
        return cls(kmod)

# pylint: disable=line-too-long
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}
    mouse_map: {(mousebutton, keymod, buttondirection): Action}

    >>> InputMapper.key_map
    {(99, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, <KeyModifier.SHIFT: 3>, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    ...

    >>> InputMapper.mouse_map
    {(<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.DOWN: 2>): <Action.START_DRAG_PLAYER: 26>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.UP: 1>): <Action.STOP_DRAG_PLAYER: 27>}
    """
    ongoing_action: OngoingAction = OngoingAction()
    key_map: dict[tuple[int,  # event.key
                        KeyModifier,  # enum wrapper on pygame kmod
                        KeyDirection  # enum -- UP or DOWN
                        ],
                  Action  # enum
                  ] = {
            (pygame.K_c,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_MORE,
            (pygame.K_k,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_LESS,
            (pygame.K_k,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_MORE,
            (pygame.K_1,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_1,
            (pygame.K_2,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_2,
            (pygame.K_3,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_3,
            (pygame.K_q,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.QUIT,
            (pygame.K_SPACE,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_PAUSE,
            (pygame.K_F11,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_FULLSCREEN,
            (pygame.K_F12,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_HUD,
            (pygame.K_EQUALS, KeyModifier.SHIFT_CTRL,  KeyDirection.DOWN):   Action.FONT_SIZE_INCREASE,
            (pygame.K_MINUS,  KeyModifier.CTRL,        KeyDirection.DOWN):   Action.FONT_SIZE_DECREASE,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_LEFT_GO,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_RIGHT_GO,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_UP_GO,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_DOWN_GO,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_LEFT_STOP,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_RIGHT_STOP,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_UP_STOP,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_DOWN_STOP,
            (pygame.K_RCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_LCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_RSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            (pygame.K_LSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            }
    # pylint: disable=line-too-long
    mouse_map: dict[tuple[MouseButton,  # enum wrapper on pygame event.button int
                          KeyModifier,  # enum wrapper on pygame kmod
                          ButtonDirection  # enum -- UP or DOWN
                          ],
                    Action  # enum
                    ] = {
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.DOWN):    Action.START_DRAG_PLAYER,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.UP):      Action.STOP_DRAG_PLAYER,
            }

    @classmethod
    def action_for_key_event(
            cls,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this key event."""
        match event.type:
            case pygame.KEYDOWN: key_direction = KeyDirection.DOWN
            case pygame.KEYUP: key_direction = KeyDirection.UP
            case _: sys.exit()  # Should never happen!
        log.debug(f"{key_direction}: {pygame.key.name(event.key)}")
        action = cls.key_map.get(
                (event.key,
                 KeyModifier.from_kmod(kmod),
                 key_direction)
                )
        log.debug(f"action: {action}")
        return action

    @classmethod
    def action_for_mouse_button_event(
            cls,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this mouse button event."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                button_direction = ButtonDirection.DOWN
                Mouse.update(event)
            case pygame.MOUSEBUTTONUP:
                button_direction = ButtonDirection.UP
                Mouse.update(event)
            case _: sys.exit()  # Should never happen!
        mouse_button = MouseButton.from_event(event)
        log.debug(f"Event MOUSEBUTTON {button_direction}, "
                  f"pos: {event.pos}, ({type(event.pos[0])}), "
                  f"event.button: {event.button}, "
                  f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
        action = cls.mouse_map.get(
                (mouse_button,
                 KeyModifier.from_kmod(kmod),
                 button_direction)
                )
        log.debug(f"action: {action}")
        return action
