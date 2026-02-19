# flake8: noqa: E501
"""Map inputs to actions.

1. See KeyModifier and ModifierKey

    Note that pygame has different codes for key modifiers and modifier keys:

        key modifiers: mod key pressed while other events happen

        modifier keys: pressing the mod key is the event

    In other words:
        I use the term "key modifier" if a modifier key is held while other things are happening.

        I use the term "modifier key" when the pressing or releasing of the modifier key itself is
        what triggers the event of interest.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
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


class ModifierKey(Enum):
    """Assign modifier keys to more specific actions.

    Modifier keys are Shift, Ctrl, and Alt. They are usually used to modify the behavior of the
    mouse or of other keys. But in the context of modifying the mouse, a KEYUP event for a modifier
    key means "stop the ongoing action". This enum class maps the modifier keys for this exact
    scenario.

    An example of mapping to a specific action:
        While "Ctrl + Click-Drag" panning, the user might release `Ctrl`. This is a KEYUP event.
        Instead of testing for pygame.K_RCTRL | pygame.K_LCTRL, we test for
        ModifierKey.RELEASE_PANNING. So we make the following mapping:

        RELEASE_PANNING = pygame.K_RCTRL | pygame.K_LCTRL

    For now I only map this to a KEYUP event. But I can imagine in the future adding something to
    indicate in the UI when CTRL is pressed. In that case I would want to act on the KEYDOWN event
    as well.

    The ModifierKey mapping is not used on its own -- it is used in the InputMapper to combine it
    with a specific KeyDirection (UP/DOWN) and KeyModifier (in case it matters that we are holding
    other modifier keys while performing this action).

    The action mapping is defined in InputMapper.modifier_key_map.
    """
    RELEASE_PANNING     = pygame.K_RCTRL | pygame.K_LCTRL
    RELEASE_DRAG_PLAYER = pygame.K_RSHIFT | pygame.K_LSHIFT


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
    modifier_key_map: dict[tuple[ModifierKey,
                                 KeyModifier,
                                 KeyDirection],
                           Action
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
            }

        self.modifier_key_map = {
            (ModifierKey.RELEASE_PANNING, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (ModifierKey.RELEASE_DRAG_PLAYER, KeyModifier.NO_MODIFIER, KeyDirection.UP): Action.STOP_DRAG_PLAYER,
            }
