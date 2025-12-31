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

    frames (int):
        For instance video_ticks, this counter increments on every iteration of the game loop.
        For instance game_ticks, this counter only increments on every iteration if game not paused.

    API:
    - In the 'Ticks.__post_init__()':
        - Define all the video frame TickCounters in dict 'video_ticks.counter'
        - Define all the game frame TickCounters in dict 'game_ticks.counter'
    - Call 'ticks.update()' to update all TickCounters.
        - Each TickCounter will look at 'Ticks.video_frames' or 'Ticks.game_frames' and decide
          whether to increment.

    >>> ticks = Ticks(clock="game")
    >>> print(ticks)
    Ticks(clock='game', frames=0,
            counter={'period_3':
                        TickCounter(ticks=..., period=3, count=0, name='period_3')})
    >>> for i in range(6):
    ...     ticks.update()
    ...     print(f"frames: {ticks.frames}")
    ...     print(f"\t{ticks.counter['period_3']}")
    frames: 1
        "period_3": count=0 (ticks every 3 frames)
    frames: 2
        "period_3": count=0 (ticks every 3 frames)
    frames: 3
        "period_3": count=1 (ticks every 3 frames)
    frames: 4
        "period_3": count=1 (ticks every 3 frames)
    frames: 5
        "period_3": count=1 (ticks every 3 frames)
    frames: 6
        "period_3": count=2 (ticks every 3 frames)
    """
    clock:      str                                     # "video" or "game"
    frames:     int = 0                                 # Count number of "video" or "game" frames
    counter:  dict[str, TickCounter] = field(init=False)  # Dict of "video" or "game" TickCounters

    def __post_init__(self) -> None:
        match self.clock:
            case "video":
                self.counter = {
                        "hud_fps": TickCounter(self, period=30, name="hud_fps"),
                        }
            case "game":
                self.counter = {
                        "period_3": TickCounter(self, period=3, name="period_3"),
                        }

    def update(self) -> None:
        """Update the tick counters"""
        self.frames += 1
        for counter in self.counter.values():
            counter.update()


@dataclass
class TickCounter:
    """Count the ticks. Each tick marks one period of something longer than one frame."""
    ticks: Ticks
    period: int
    count: int = 0
    name: str = "NameMe"

    def __str__(self) -> str:
        return f"\"{self.name}\": count={self.count} (ticks every {self.period} frames)"

    @property
    def is_period(self) -> bool:
        """True when a whole number of periods has elapsed."""
        ticks = self.ticks
        return (ticks.frames % self.period) == 0

    def update(self) -> None:
        """Update the counter when a period has elapsed."""
        if self.is_period:
            self.count += 1
