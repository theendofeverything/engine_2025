# flake8: noqa: E501
"""Map inputs to actions.

Note that pygame has two different codes for modifier keys depending on usage. For example:
    pygame.K_RSHIFT -- Code to check if the Right-Shift key is having its own KEYDOWN or KEYUP event
    pygame.KMOD_RSHIFT -- Code to check if Right-Shift is modifying another event
"""

from __future__ import annotations
from enum import Enum, auto
import sys
import logging
import pygame
from src.context import namespace
from engine.mouse import Mouse, ButtonName, ButtonDirection

log = logging.getLogger(__name__)


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
@namespace
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
    {(<ButtonName.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<ButtonName.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<ButtonName.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<ButtonName.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<ButtonName.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.DOWN: 2>): <Action.START_DRAG_PLAYER: 26>,
    (<ButtonName.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.UP: 1>): <Action.STOP_DRAG_PLAYER: 27>}
    """
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
    mouse_map: dict[tuple[ButtonName,  # enum wrapper on pygame event.button int
                          KeyModifier,  # enum wrapper on pygame kmod
                          ButtonDirection  # enum -- UP or DOWN
                          ],
                    Action  # enum
                    ] = {
            (ButtonName.LEFT,   KeyModifier.PANNING,     ButtonDirection.DOWN): Action.START_PANNING,
            (ButtonName.LEFT,   KeyModifier.PANNING,     ButtonDirection.UP):   Action.STOP_PANNING,
            (ButtonName.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.DOWN): Action.START_PANNING,
            (ButtonName.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.UP):   Action.STOP_PANNING,
            (ButtonName.LEFT,   KeyModifier.SHIFT,    ButtonDirection.DOWN):    Action.START_DRAG_PLAYER,
            (ButtonName.LEFT,   KeyModifier.SHIFT,    ButtonDirection.UP):      Action.STOP_DRAG_PLAYER,
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
        mouse_button = ButtonName.from_event(event)
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
