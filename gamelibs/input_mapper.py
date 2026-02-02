#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Map inputs to actions.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import pygame


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


class KeyDirection(Enum):
    """Enumerate names for KEYUP and KEYDOWN instead of just using bool."""
    UP = auto()
    DOWN = auto()


@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, 0, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, 0, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, 3, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    ...
    (1073741905, 0, <KeyDirection.UP: 1>): <Action.PLAYER_MOVE_DOWN_STOP: 23>}
    """
    key_map: dict[tuple[int, int, KeyDirection], Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        no_modifier = pygame.KMOD_NONE
        shift = pygame.KMOD_SHIFT
        ctrl = pygame.KMOD_CTRL
        shift_ctrl = pygame.KMOD_SHIFT | pygame.KMOD_CTRL

        self.key_map = {
            (pygame.K_c,      no_modifier, KeyDirection.DOWN): Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d,      no_modifier, KeyDirection.DOWN): Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b,      shift,       KeyDirection.DOWN): Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b,      no_modifier, KeyDirection.DOWN): Action.CONTROLS_ADJUST_B_MORE,
            (pygame.K_k,      shift,       KeyDirection.DOWN): Action.CONTROLS_ADJUST_K_LESS,
            (pygame.K_k,      no_modifier, KeyDirection.DOWN): Action.CONTROLS_ADJUST_K_MORE,
            (pygame.K_1,      no_modifier, KeyDirection.DOWN): Action.CONTROLS_PICK_MODE_1,
            (pygame.K_2,      no_modifier, KeyDirection.DOWN): Action.CONTROLS_PICK_MODE_2,
            (pygame.K_3,      no_modifier, KeyDirection.DOWN): Action.CONTROLS_PICK_MODE_3,
            (pygame.K_q,      no_modifier, KeyDirection.DOWN): Action.QUIT,
            (pygame.K_SPACE,  no_modifier, KeyDirection.DOWN): Action.TOGGLE_PAUSE,
            (pygame.K_F11,    no_modifier, KeyDirection.DOWN): Action.TOGGLE_FULLSCREEN,
            (pygame.K_F12,    no_modifier, KeyDirection.DOWN): Action.TOGGLE_DEBUG_HUD,
            (pygame.K_EQUALS, shift_ctrl,  KeyDirection.DOWN): Action.FONT_SIZE_INCREASE,
            (pygame.K_MINUS,  ctrl,        KeyDirection.DOWN): Action.FONT_SIZE_DECREASE,
            (pygame.K_LEFT,   no_modifier, KeyDirection.DOWN): Action.PLAYER_MOVE_LEFT_GO,
            (pygame.K_RIGHT,  no_modifier, KeyDirection.DOWN): Action.PLAYER_MOVE_RIGHT_GO,
            (pygame.K_UP,     no_modifier, KeyDirection.DOWN): Action.PLAYER_MOVE_UP_GO,
            (pygame.K_DOWN,   no_modifier, KeyDirection.DOWN): Action.PLAYER_MOVE_DOWN_GO,
            (pygame.K_LEFT,   no_modifier, KeyDirection.UP):   Action.PLAYER_MOVE_LEFT_STOP,
            (pygame.K_RIGHT,  no_modifier, KeyDirection.UP):   Action.PLAYER_MOVE_RIGHT_STOP,
            (pygame.K_UP,     no_modifier, KeyDirection.UP):   Action.PLAYER_MOVE_UP_STOP,
            (pygame.K_DOWN,   no_modifier, KeyDirection.UP):   Action.PLAYER_MOVE_DOWN_STOP,
            }
