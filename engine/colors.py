"""Name the colors used in the game.
"""
from dataclasses import dataclass
from pygame.color import Color


@dataclass
class Colors:
    """Color names"""
    background:     Color = Color(30, 60, 90)
    line:           Color = Color(120, 90, 30)
    line_debug:     Color = Color(200, 50, 50)
    text:           Color = Color(255, 255, 255)
