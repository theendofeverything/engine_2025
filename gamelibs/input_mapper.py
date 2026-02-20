# flake8: noqa: E501
"""Map inputs to actions.

Note that pygame has two different codes for modifier keys depending on usage. For example:
    pygame.K_RSHIFT -- Code to check if the Right-Shift key is having its own KEYDOWN or KEYUP event
    pygame.KMOD_RSHIFT -- Code to check if Right-Shift is modifying another event
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import sys
import logging
import pygame
from engine.ui import MouseButton


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


class ButtonDirection(Enum):
    """Enumerate names for MOUSEBUTTONUP and MOUSEBUTTONDOWN."""
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
@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}
    mouse_map: {(mousebutton, keymod, buttondirection): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, <KeyModifier.SHIFT: 3>, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    ...
    (1073741905, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.UP: 1>): <Action.PLAYER_MOVE_DOWN_STOP: 23>}

    >>> mouse_map = input_mapper.mouse_map
    >>> mouse_map
    {(<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER : 0>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.DOWN: 2>): <Action.START_DRAG_PLAYER: 26>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.UP: 1>): <Action.STOP_DRAG_PLAYER: 27>}
    """
    key_map: dict[tuple[int,  # event.key
                        KeyModifier,  # enum wrapper on pygame kmod
                        KeyDirection  # enum -- UP or DOWN
                        ],
                  Action  # enum
                  ] = field(default_factory=dict)
    mouse_map: dict[tuple[MouseButton,  # enum wrapper on pygame event.button int
                          KeyModifier,  # enum wrapper on pygame kmod
                          ButtonDirection  # enum -- UP or DOWN
                          ],
                    Action  # enum
                    ] = field(default_factory=dict)

    # pylint: disable=line-too-long
    def __post_init__(self) -> None:
        self.mouse_map = {
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.DOWN):    Action.START_DRAG_PLAYER,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.UP):      Action.STOP_DRAG_PLAYER,
            }

        self.key_map = {
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

    def action_for_key_event(
            self,
            log: logging.Logger,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this key event."""
        input_mapper = self
        match event.type:
            case pygame.KEYDOWN: key_direction = KeyDirection.DOWN
            case pygame.KEYUP: key_direction = KeyDirection.UP
            case _: sys.exit()  # Should never happen!
        log.debug(f"{key_direction}: {pygame.key.name(event.key)}")
        action = input_mapper.key_map.get(
                (event.key,
                 KeyModifier.from_kmod(kmod),
                 key_direction)
                )
        log.debug(f"action: {action}")
        return action
