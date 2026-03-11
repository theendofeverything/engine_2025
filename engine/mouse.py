#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Track mouse state in a Module Namespace Class.

API
---

- mouse.ButtonName: IntEnum -- Name all the mouse buttons
- mouse.is_pressed(btn: mouse.ButtonName) -- Return True/False if button is pressed or not
- mouse.ButtonDirection: Enum -- UP/DOWN for mapping the button event to the appropriate action
- mouse.update(event: pygame.event.Event) -- Keep the mouse button state up to date. Do this any time you handle a mouse event, for example:

        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                button_direction = mouse.ButtonDirection.DOWN
                mouse.update(event)
            case pygame.MOUSEBUTTONUP:
                button_direction = mouse.ButtonDirection.UP
                mouse.update(event)

'mouse.update(event)' updates the internal `_state` dict of button values. My intent is for the user
to use `update()` instead of writing to `_state` directly.


Examples
--------

Button state begins with no buttons pressed:
>>> from engine import mouse
>>> mouse.is_pressed(mouse.ButtonName.LEFT)
False

Simulate a left-click:
>>> event = pygame.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})

Update the button state:
>>> mouse.update(event)

Check that we have updated the state of the left mouse button:
>>> mouse.is_pressed(mouse.ButtonName.LEFT)
True

Convert pygame.Event.button 'int' type to a ButtonName Enum:
>>> mouse_button = mouse.ButtonName.from_event(event)

Print the button state (TRUE) using its name (LEFT) instead of its value (1):
>>> print(f"mouse.is_pressed({mouse_button.name}): {mouse.is_pressed(mouse_button)}")
mouse.is_pressed(LEFT): True

Note the use of 'ButtonName' vs 'ButtonName.name':
    - 'ButtonName' gets the 'int' value (1, 2, etc.)
    - 'ButtonName.name' gets the button name ('LEFT', 'MIDDLE', etc.)
"""

from __future__ import annotations
from enum import Enum, IntEnum, auto
import pygame


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


# Store states for all 5 buttons: Pressed (True) and NotPressed (False)
_state = {button.value: False for button in ButtonName}


def update(event: pygame.Event) -> None:
    """Update the state of all buttons in ButtonName."""
    match event.type:
        case pygame.MOUSEBUTTONDOWN:
            _state[event.button] = True
        case pygame.MOUSEBUTTONUP:
            _state[event.button] = False


def is_pressed(button: ButtonName) -> bool:
    """Return True/False if button ButtonName is pressed.

    If the "button" does not exist, return False instead of None:
    >>> from engine import mouse
    >>> mouse.is_pressed(6)
    False
    """
    return _state.get(button, False)
