"""Buffer integer values.

BufferInt works like a shift register that holds one value:
- The input is free to change at any time, but this does not affect the output.
- The output holds its previous value until the input is clocked in.

Usage:
    Use 'BufferInt' in class 'FOO' to provide buffered access to attribute 'BAR' of 'FOO'.
    1. Add attribute '_BAR_buffer: BufferInt = BufferInt()'
    2. Create an API in 'FOO' with these two methods:
        FOO.update_buffered_BAR(val):
            Clock value 'val' into 'FOO._BAR_buffer'.
        FOO.BAR_buffered:
            @property to access 'FOO._BAR_buffer.value'
    Now the 'Game' can use a timer (such as a 'TickCounter' in 'Ticks') to decide when the to clock
    new values into 'FOO._BAR_buffer'.

Example:
    The FPS is updated on very iteration of the game loop, which means if we display this directly
    in the HUD it (sometimes) changes very rapidly, making it hard to read. The solution is to
    buffer the FPS before displaying it in the HUD.

    The FPS data is contained in 'Timing'. 'Timing' uses 'BufferInt' to create a buffered version of
    milliseconds per video frame for display in the HUD. 'Timing' creates the API for 'Game' to use.

    class Timing:
        ...
        ms_per_frame:           int = 16                    # Initial value for debug HUD
        _ms_per_frame_buffer:   BufferInt = BufferInt()     # BUFFERED ACCESS TO ms_per_frame

        def __post_init__(self) -> None:
            self.update_buffered_ms_per_frame()             # INITIALIZE BUFFERED VALUE

        def update_buffered_ms_per_frame(self) -> None:
            self._ms_per_frame_buffer.load(self.ms_per_frame)   # LOAD VALUE OF ms_per_frame
            self._ms_per_frame_buffer.clock()                   # CLOCK VALUE INTO BUFFER

        @property
        def ms_per_frame_buffered(self) -> int:
            return self._ms_per_frame_buffer.value          # READ THE BUFFERED VALUE

    And since 'fps' is a calculated value, this also gives me a buffered version of FPS
    (without needing a 'BufferFloat'):

        @property
        def fps(self) -> float:
            return 1000/self.ms_per_frame

        @property
        def fps_buffered(self) -> float:
            return 1000/self._ms_per_frame_buffer.value     # BUFFERED FPS

    'Game' displays the buffered values in the HUD.
    'Game' gets buffered access from the API 'timing.fps_buffered':

            fps = timing.fps_buffered
            ms_per_frame = timing.ms_per_frame_buffered
            debug.hud.print(f"|\n+- FPS: {fps:0.1f}, frame period: {ms_per_frame:d}ms")

    'Game' uses 'Ticks' to check when to update the buffered values.
    'Game' updates the buffer with 'timing.update_buffered_ms_per_frame()':

            if timing.ticks.counter["hud_fps"].is_period:
                timing.update_buffered_ms_per_frame()
"""

from dataclasses import dataclass


@dataclass
class BufferInt:
    """Buffer ints.

    >>> buffer = BufferInt()
    >>> buffer
    BufferInt(_value=0, _value_next=0)

    >>> buffer.load(42)
    >>> buffer
    BufferInt(_value=0, _value_next=42)

    >>> buffer.clock()
    >>> buffer
    BufferInt(_value=42, _value_next=42)
    """
    _value: int = 0
    _value_next: int = 0

    @property
    def value(self) -> int:
        """Return the most recently clocked-in value."""
        return self._value

    def load(self, val: int) -> None:
        """Load value 'val' to be clocked in on next clock."""
        self._value_next = val

    def clock(self) -> None:
        """Clock in the loaded value."""
        self._value = self._value_next
