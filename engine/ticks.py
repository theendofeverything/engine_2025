"""Track frame count for clocking animations.

Game uses Ticks.
Ticks defines the TickCounters in the game. Each animation gets its own TickCounter.

TODO: come up with a strategy for resetting Ticks.frames when it gets very large.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Ticks:
    """Count frames for clocking animations.

    >>> ticks = Ticks()
    >>> print(ticks)
    Ticks(frames=0, t1=TickCounter(ticks=..., period=3, count=0, name='t1'), ...)
    >>> for i in range(6):
    ...     ticks.update()
    ...     print(ticks)
    Ticks(frames=1, t1=TickCounter(ticks=..., period=3, count=0, name='t1'), ...)
    Ticks(frames=2, t1=TickCounter(ticks=..., period=3, count=0, name='t1'), ...)
    Ticks(frames=3, t1=TickCounter(ticks=..., period=3, count=1, name='t1'), ...)
    Ticks(frames=4, t1=TickCounter(ticks=..., period=3, count=1, name='t1'), ...)
    Ticks(frames=5, t1=TickCounter(ticks=..., period=3, count=1, name='t1'), ...)
    Ticks(frames=6, t1=TickCounter(ticks=..., period=3, count=2, name='t1'), ...)
    """
    # game: Game
    frames: int = 0                                     # Count number of frames
    t1: TickCounter = field(init=False)                 # Count number of thing 1
    hud_fps: TickCounter = field(init=False)            # Tick to update FPS in HUD

    def __post_init__(self) -> None:
        # Thing 1 has a period of 3 frames
        self.t1 = TickCounter(self, period=3, name="t1")
        self.hud_fps = TickCounter(self, period=30, name="hud_fps")

    def update(self) -> None:
        """Update the ticks"""
        self.frames += 1
        self.t1.update()
        self.hud_fps.update()


@dataclass
class TickCounter:
    """Count the ticks. Each tick marks one period of something longer than one frame."""
    ticks: Ticks
    period: int
    count: int = 0
    name: str = "NameMe"

    def __str__(self) -> str:
        return f"{self.name}({self.period} frames): {self.count}"

    @property
    def is_period(self) -> bool:
        """True when a whole number of periods has elapsed."""
        ticks = self.ticks
        return (ticks.frames % self.period) == 0

    def update(self) -> None:
        """Update the counter when a period has elapsed."""
        if self.is_period:
            self.count += 1
