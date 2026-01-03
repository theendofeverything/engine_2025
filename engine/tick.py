"""Track frame count for clocking animations.

Game.Timing creates a dictionary of Ticks.
Each Tick creates a dictionary of TickCounters in the game.
Each animation gets its own TickCounter.

TODO: come up with a strategy for resetting Ticks.frames when it gets very large.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Tick:
    """Count frames for clocking animations.

    frames (int):
        The engine counts video frames and game frames separately:
        - Timing.ticks["video"] -- video Tick:
            (video) Tick.frames: a counter that increments on every iteration of the game loop
        - Timing.ticks["game"] -- game Tick:
            (game) Tick.frames: a counter that only increments on every iteration if game NOT
            paused.

    API:
        Setup:
        - In the 'Timing.__post_init__()':
            - Define all the video frame TickCounters in dict 'Timing.ticks["video"].counters'
            - Define all the game frame TickCounters in dict 'Timing.ticks["game"].counters'
        Usage:
        - Call 'tick.update()' to update all TickCounters.
            - Each TickCounter will look at:
                (video) Tick.frames -- 'Timing.ticks["video"].frames'
                or
                (game) Tick.frames -- 'Timing.ticks["game"].frames'
              and decide whether to increment itself.
        - TickCounter.is_period:
            - True when a whole number of periods has elapsed
        - TickCounter.count:
            - The number of clock ticks so far

    >>> tick = Tick()
    >>> print(tick)
    Tick(frames=0, counters={})
    >>> tick.counters = {"period_2": TickCounter(tick, period=2, name="period_2")}
    >>> for i in range(4):
    ...     tick.update()
    ...     print(f"frames: {tick.frames}")
    ...     print(f"\t{tick.counters['period_2']}")
    frames: 1
        "period_2": count=0 (ticks every 2 frames)
    frames: 2
        "period_2": count=1 (ticks every 2 frames)
    frames: 3
        "period_2": count=1 (ticks every 2 frames)
    frames: 4
        "period_2": count=2 (ticks every 2 frames)
    """
    frames:   int = 0                                   # Count number of "video" or "game" frames
    counters: dict[str, TickCounter] = field(init=False)  # Dict of "video" or "game" TickCounters

    def __post_init__(self) -> None:
        # Assign an empty dict in case this is instantiated outside of Timers (like in unit tests)
        self.counters = {}

    def update(self) -> None:
        """Update the tick counters."""
        tick = self
        tick.frames += 1
        for tick_counter in tick.counters.values():
            tick_counter.update()


@dataclass
class TickCounter:
    """Count the ticks. Each tick marks one period of something longer than one frame."""
    tick: Tick
    period: int
    count: int = 0
    name: str = "NameMe"

    def __str__(self) -> str:
        return f"\"{self.name}\": count={self.count} (ticks every {self.period} frames)"

    @property
    def is_period(self) -> bool:
        """True when a whole number of periods has elapsed."""
        frames = self.tick.frames
        return (frames % self.period) == 0

    def update(self) -> None:
        """Update the counter if a whole number of periods has elapsed."""
        if self.is_period:
            self.count += 1


# NOT USED
class Clk(Enum):
    """Clock signals can be LOW or HIGH."""
    LOW = 0
    HIGH = 1


# NOT USED
@dataclass
class TickCounterWithClock:
    """Count the ticks. Each tick marks one period of something longer than one frame.

    Stateful Attributes:
        period (int):
            Number of tick.frames it takes to increment count.
        count (int):
            Number of periods that have elapsed since the game started.
        _clk (bool):
            A ripple-counter-like mechanism (see ASCII-art sketch in the update() docstring) to
            guarantee the TickCounter only runs its 'update()' once per period:
                - Transition False to True when tick.frames % period is zero.
                - Transition True to False when tick.frames % period is NOT zero.

    Calculated Attributes:
        _is_period (bool):
            True when the number of tick.frames % period is zero. False otherwise.
        clocked (bool):
            True while _clk is HIGH.
    """
    tick: Tick
    period: int
    count: int = 0
    name: str = "NameMe"
    _clk: Clk = Clk.LOW                                 # To guarantee one update per period

    def __str__(self) -> str:
        return f"\"{self.name}\": count={self.count} (ticks every {self.period} frames)"

    @property
    def clocked(self) -> bool:
        """True when a whole period has just elapsed, then returns False on next update."""
        return self._clk == Clk.HIGH

    @property
    def _is_period(self) -> bool:
        """True when a whole number of periods has elapsed."""
        frames = self.tick.frames
        return (frames % self.period) == 0

    def update(self) -> None:
        """Update the counter (once) when a period has elapsed.

                      UPDATE
            RETURN    ──┬───
             ▲          │
             │          ▼
             │  ┌────────────┐ YES
             │  │ IS PERIOD? ├────────────┐
             │  └───────┬────┘            ▼
             │          │ NO      ┌─────────────┐ YES
             │          │         │ IS CLK LOW? ├────────────┐
             │          ▼         └───────┬─────┘            ▼
             │       ┌─────┐              │NO             ┌─────┐
             │ LOW──▶│ CLK │              │        HIGH──▶│ CLK │
             │       └──┬──┘              │               └──┬──┘
             │          │                 │                  │
             │          │                 │                  ▼
             │          │                 │               ┌───────┐
             │          │                 │               │ CNT++ │
             │          │                 │               └──┬────┘
             └──────────┘◀────────────────┘◀─────────────────┘
        """
        if self._is_period:
            if self._clk == Clk.LOW:
                self._clk = Clk.HIGH
                self.count += 1
            else:
                pass
        else:
            self._clk = Clk.LOW
