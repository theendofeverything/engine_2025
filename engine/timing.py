"""Timing is a helper struct to organize Game. It contains all things relating to time: game clock,
frame period.
"""
from dataclasses import dataclass
import pygame
from .ticks import Ticks


@dataclass
class Timing:
    """All time-related game instance attributes."""
    clock:                  pygame.time.Clock = pygame.time.Clock()
    ms_per_frame:           int = 16                    # Initial value for debug HUD
    ticks:                  Ticks = Ticks()             # Track frames for clocking animations
    is_paused:              bool = False                # Track if game is paused
