"""Name the colors used in the game.
"""
from dataclasses import dataclass
from pygame.color import Color


@dataclass
class Colors:
    """Color names

    Do not instantiate. Use as a name-spaced constant:
    >>> Colors.text
    Color(255, 255, 255, 255)
    """
    background:     Color = Color(30, 60, 90)
    background_lines: Color = Color(60, 90, 120)
    line:           Color = Color(120, 150, 60)
    line_player:    Color = Color(120, 150, 255)
    line_debug:     Color = Color(200, 50, 50)
    text:           Color = Color(255, 255, 255)
    panning:        Color = Color(255, 200, 200)
