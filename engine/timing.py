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
    ticks:                  Ticks = Ticks()             # Track frames for clocking animations
    is_paused:              bool = False                # Track if game is paused
    ms_per_frame:           int = 16                    # Initial value for debug HUD

    def maintain_framerate(self, fps: int = 60) -> None:
        """Maintain the desired fps framerate using pygame.time.Clock.tick().

        This updates the internally tracked milliseconds per frame.
        """
        self.ms_per_frame = self.clock.tick(fps)

    @property
    def fps(self) -> float:
        """Frames per second."""
        return 1000/self.ms_per_frame
