"""Timing is a helper struct to organize Game. It contains all things relating to time: game clock,
frame period.
"""
from dataclasses import dataclass, field
import pygame
from .tick import Tick, TickCounter
from .buffer_value import BufferInt


@dataclass
class Timing:
    """All time-related game instance attributes."""
    clock:                  pygame.time.Clock = pygame.time.Clock()
    ticks:                  dict[str, Tick] = field(init=False)  # TickCounters for game and video
    is_paused:              bool = False                # Track if game is paused
    ms_per_frame:           int = 16                    # Initial value for debug HUD
    _ms_per_frame_buffer:   BufferInt = BufferInt()     # Buffered value

    def __post_init__(self) -> None:
        self.update_buffered_ms_per_frame()
        self.ticks = {}
        self.ticks["game"] = Tick()
        self.ticks["video"] = Tick()
        for name, tick in self.ticks.items():
            match name:
                case "video":
                    tick.counters = {
                            "hud_fps": TickCounter(tick, period=30),
                            }
                case "game":
                    tick.counters = {
                            "period_3": TickCounter(tick, period=3),
                            }
        # Assign each tick_counter dict key to its TickCounter.name for display in the debug HUD.
        for tick in self.ticks.values():
            for name, tick_counter in tick.counters.items():
                tick_counter.name = name

    def update_buffered_ms_per_frame(self) -> None:
        """Update the buffered value to hold the initial value of milliseconds per frame."""
        self._ms_per_frame_buffer.load(self.ms_per_frame)
        self._ms_per_frame_buffer.clock()

    def maintain_framerate(self, fps: int = 60) -> None:
        """Maintain the desired fps framerate using pygame.time.Clock.tick().

        This updates the internally tracked milliseconds per frame.
        """
        self.ms_per_frame = self.clock.tick(fps)

    @property
    def fps(self) -> float:
        """Frames per second."""
        return 1000/self.ms_per_frame

    @property
    def ms_per_frame_buffered(self) -> int:
        """Buffered version of milliseconds per frame."""
        return self._ms_per_frame_buffer.value

    @property
    def fps_buffered(self) -> float:
        """Buffered version of frames per second."""
        return 1000/self._ms_per_frame_buffer.value
