"""Timing is a helper struct to organize Game. It contains all things relating to time: game clock,
frame period.
"""
from dataclasses import dataclass
import pygame


@dataclass
class Timing:
    """All time-related game instance attributes."""
    clock:                  pygame.time.Clock = pygame.time.Clock()
    ms_per_frame:           int = 16                    # Initial value for debug HUD
