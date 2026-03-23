"""Name the colors used in the game.
"""

from typing import TypeAlias

Color: TypeAlias = tuple[int, int, int]


# pylint: disable=too-few-public-methods
class Colors:
    """Color names

    Do not instantiate. Use as a name-spaced constant:
    >>> Colors.text
    Color(255, 255, 255, 255)
    """
    background:     Color = (30, 60, 90)
    background_lines: Color = (60, 90, 120)
    line:           Color = (120, 150, 60)
    line_player:    Color = (120, 150, 255)
    line_debug:     Color = (200, 50, 50)
    text:           Color = (255, 255, 255)
    panning:        Color = (255, 200, 200)
