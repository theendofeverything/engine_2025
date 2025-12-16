"""Panning is a helper struct to organize Game. It tracks all state for panning: panning.start,
panning.end, panning.amount.
"""
from dataclasses import dataclass
from .geometry_types import Point2D, Vec2D


@dataclass
class Panning:
    """Track panning state.

    >>> panning = Panning()                             # Track panning state
    >>> mouse_pos = (123, 456)                          # Position when button 1 was pressed
    >>> panning.start = Point2D.from_tuple(mouse_pos)   # Track panning start position
    >>> mouse_pos = (246, 456)                          # Position later while still panning
    >>> panning.end = Point2D.from_tuple(mouse_pos)     # Track latest panning position
    >>> panning.vector                                  # Report the latest panning vector
    Vec2D(x=123, y=0)
    """
    end:                    Point2D = Point2D(0, 0)     # Dummy initial value
    is_active:              bool = False

    def __post_init__(self) -> None:
        self.start = self.end                           # Zero-out the panning vector

    @property
    def vector(self) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=self.start, end=self.end)
