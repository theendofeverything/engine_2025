"""Timing is a helper struct to organize Game.

Timing contains all things relating to time:

- the game clock: pygame.time.Clock()
- the frame rate metrics: FPS and frame period
- dictionary of frame counters:
    - "video" frame counters
    - "game" frame counters

"Video" frames are always incrementing, while "game" frames only increment when the game is not
paused.

The frame counters maintain:
- frame_count: the number of frames so far
- is_paused: whether or not this frame counter is paused (only applies to "game" so far)
- dictionary of clocked events: names of events that update (get clocked) once every N frames

The clocked events maintain:
- period: the number of frames required to clock this event
- event_count: the number of times this event has been clocked (number of times it has happened)
- event_name: the name of the event (the name is already in the dictionary key, but copying this in
  as an attribute is useful for debug purposes because I can print a clocked event and see its name
  without iterating through the dictionary)

TODO: come up with a strategy for resetting FrameCounter.frame_count and ClockedEvent.event_count
when these numbers get very large.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import pygame
from .buffer_value import BufferInt


@dataclass
class ClockedEvent:
    """Trigger an event every time some number of frames elapses.

    API:
        is_period: True when it is time for the event to happen.

    Internal API:
        update(): ClockedEvents are updated by their FrameCounter. The FrameCounter calls 'update()'
        on all of its clocked events.
    """
    frame_counter: FrameCounter                         # How the ClockedEvent gets the frame_count
    period: int                                         # Number of frames
    event_count: int = 0                                # Number of times event has happened
    event_name: str = "NameMe"                          # Auto-populated in Timing.__post_init__()

    def __str__(self) -> str:
        return (f"\"{self.event_name}\": "
                f"event_count={self.event_count} "
                f"(clocked every {self.period} frames)"
                )

    @property
    def frame_count(self) -> int:
        """The number of frames counted by the FrameCounter."""
        return self.frame_counter.frame_count

    @property
    def is_period(self) -> bool:
        """True when a whole number of periods has elapsed."""
        return (self.frame_count % self.period) == 0

    def update(self) -> None:
        """Update the event counter if a whole number of periods has elapsed."""
        if self.is_period:
            self.event_count += 1


@dataclass
class FrameCounter:
    """Count frames for clocking animations.

    frame_count (int):
        The engine counts video frames and game frames separately:
        - Timing.frame_counters["video"]:
            counter that increments on every iteration of the game loop
        - Timing.frame_counters["game"]:
            counter that only increments on every iteration if game NOT paused

    is_paused (bool):
        Track whether the frame counter is paused.

    clocked_events (dict[str, ClockedEvent]):
        Dictionary of events clocked by this frame counter. Each clocked event defines its own
        period (number of frames) for when the event should happen.

    API:

        Setup:
        - In the 'Timing.__post_init__()':
            - Define all the events clocked by video frames in dict
              'Timing.frame_counters["video"].clocked_events'
            - Define all the events clocked by game frames in dict
              'Timing.frame_counters["game"].clocked_events'

        Usage:
        - Call 'frame_counter.update()' to update the frame count and all clocked_events.

    >>> frame_counter = FrameCounter()
    >>> print(frame_counter)
    FrameCounter(frame_count=0, is_paused=False, clocked_events={})
    >>> frame_counter.clocked_events = {"period_2": ClockedEvent(
    ... frame_counter, period=2, event_name="period_2")}
    >>> for i in range(4):
    ...     frame_counter.update()
    ...     print(f"frame_count: {frame_counter.frame_count}")
    ...     print(f"\t{frame_counter.clocked_events['period_2']}")
    frame_count: 1
        "period_2": event_count=0 (clocked every 2 frames)
    frame_count: 2
        "period_2": event_count=1 (clocked every 2 frames)
    frame_count: 3
        "period_2": event_count=1 (clocked every 2 frames)
    frame_count: 4
        "period_2": event_count=2 (clocked every 2 frames)

    Compare with a period of 1 (event clocked every video frame) to convince myself this works as it
    should.
    >>> frame_counter = FrameCounter()
    >>> frame_counter.clocked_events = {"period_1": ClockedEvent(
    ... frame_counter, period=1, event_name="period_1")}
    >>> for i in range(4):
    ...     frame_counter.update()
    ...     print(f"frame_count: {frame_counter.frame_count}")
    ...     print(f"\t{frame_counter.clocked_events['period_1']}")
    frame_count: 1
        "period_1": event_count=1 (clocked every 1 frames)
    frame_count: 2
        "period_1": event_count=2 (clocked every 1 frames)
    frame_count: 3
        "period_1": event_count=3 (clocked every 1 frames)
    frame_count: 4
        "period_1": event_count=4 (clocked every 1 frames)
    """
    frame_count: int = 0
    is_paused: bool = False
    clocked_events: dict[str, ClockedEvent] = field(init=False)

    def __post_init__(self) -> None:
        # Assign an empty dict for when this is instantiated outside of Timing
        # (like in FrameCounter unit tests)
        self.clocked_events = {}

    def update(self) -> None:
        """Update the frame count and the clocked events."""
        if not self.is_paused:
            self.frame_count += 1
            for clocked_event in self.clocked_events.values():
                clocked_event.update()

    def toggle_pause(self) -> None:
        """Toggle is_paused."""
        self.is_paused = not self.is_paused


@dataclass
class Timing:
    """All time-related game instance attributes."""
    clock:                  pygame.time.Clock = pygame.time.Clock()
    frame_counters:         dict[str, FrameCounter] = field(init=False)
    ms_per_frame:           int = 16                    # Initial value for debug HUD
    _ms_per_frame_buffer:   BufferInt = BufferInt()     # Buffered value

    def __post_init__(self) -> None:
        self.frame_counters = {}
        self.frame_counters["video"] = FrameCounter()
        self.frame_counters["game"] = FrameCounter()
        for name, frame_counter in self.frame_counters.items():
            match name:
                case "video":
                    frame_counter.clocked_events["hud_fps"] = ClockedEvent(
                            frame_counter,
                            period=30
                            )
                case "game":
                    frame_counter.clocked_events["period_1"] = ClockedEvent(
                            frame_counter,
                            period=1
                            )
                    frame_counter.clocked_events["period_2"] = ClockedEvent(
                            frame_counter,
                            period=2
                            )
                    frame_counter.clocked_events["period_3"] = ClockedEvent(
                            frame_counter,
                            period=3
                            )
        # Assign each clocked_event dict key to its ClockedEvent.event_name
        # for display in the debug HUD.
        for frame_counter in self.frame_counters.values():
            for name, clocked_event in frame_counter.clocked_events.items():
                clocked_event.event_name = name

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
