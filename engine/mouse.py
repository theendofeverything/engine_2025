#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Mouse
"""

from __future__ import annotations
from enum import Enum, IntEnum, auto
import pygame
from src.context import namespace


class ButtonName(IntEnum):
    """Enumerate the mouse button values from pygame.Event.button.

    >>> ButtonName.LEFT
    <ButtonName.LEFT: 1>
    """
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5

    @classmethod
    def from_event(cls, event: pygame.Event) -> ButtonName:
        """Get ButtonName from an event (uses event.button)."""
        return cls(event.button)


class ButtonDirection(Enum):
    """Enumerate names for MOUSEBUTTONUP and MOUSEBUTTONDOWN."""
    UP = auto()
    DOWN = auto()


@namespace
class Mouse:
    """Track mouse state in a Namespace Class.

    Button state begins with no buttons pressed:
    >>> Mouse.is_pressed(ButtonName.LEFT)
    False

    Simulate a left-click:
    >>> event = pygame.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})

    Update the button state:
    >>> Mouse.update(event)

    Check that we have updated the state of the left mouse button:
    >>> Mouse.is_pressed(ButtonName.LEFT)
    True

    Convert pygame.Event.button 'int' type to a ButtonName Enum:
    >>> mouse_button = ButtonName.from_event(event)

    Print the button state (TRUE) using its name (LEFT) instead of its value (1):
    >>> print(f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
    Mouse.is_pressed(LEFT): True

    Note the use of 'ButtonName' vs 'ButtonName.name':
        - 'ButtonName' gets the 'int' value (1, 2, etc.)
        - 'ButtonName.name' gets the button name ('LEFT', 'MIDDLE', etc.)
    """
    # Store states for all 5 buttons: Pressed (True) and NotPressed (False)
    _state = {button.value: False for button in ButtonName}

    @classmethod
    def update(cls, event: pygame.Event) -> None:
        """Update the state of all buttons in ButtonName."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                cls._state[event.button] = True
            case pygame.MOUSEBUTTONUP:
                cls._state[event.button] = False

    @classmethod
    def is_pressed(cls, button: ButtonName) -> bool:
        """Return True/False if button ButtonName is pressed.

        If the "button" does not exist, return False instead of None:
        >>> Mouse.is_pressed(6)
        False
        """
        return cls._state.get(button, False)
