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


@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, 0): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, 0): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,...
    (45, 128): <Action.FONT_SIZE_DECREASE: 8>}
    """
    key_map: dict[tuple[int, int], Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # TODO: I put all variations of left and right SHIFT and CTRL keys but this is insanity.
        # There has to be a better way.
        self.key_map = {
            (pygame.K_c, pygame.KMOD_NONE): Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d, pygame.KMOD_NONE): Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b, pygame.KMOD_SHIFT): Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b, pygame.KMOD_NONE): Action.CONTROLS_ADJUST_B_MORE,
            (pygame.K_k, pygame.KMOD_SHIFT): Action.CONTROLS_ADJUST_K_LESS,
            (pygame.K_k, pygame.KMOD_NONE): Action.CONTROLS_ADJUST_K_MORE,
            (pygame.K_1, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_1,
            (pygame.K_2, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_2,
            (pygame.K_3, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_3,
            (pygame.K_q, pygame.KMOD_NONE): Action.QUIT,
            (pygame.K_SPACE, pygame.KMOD_NONE): Action.TOGGLE_PAUSE,
            (pygame.K_F11, pygame.KMOD_NONE): Action.TOGGLE_FULLSCREEN,
            (pygame.K_F12, pygame.KMOD_NONE): Action.TOGGLE_DEBUG_HUD,
            (pygame.K_EQUALS, pygame.KMOD_SHIFT | pygame.KMOD_CTRL): Action.FONT_SIZE_INCREASE,
            (pygame.K_MINUS, pygame.KMOD_CTRL): Action.FONT_SIZE_DECREASE,
            }
