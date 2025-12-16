"""Panning is a helper struct to organize Game. It tracks all state for panning: panning.start,
panning.end, panning.amount.
"""
from dataclasses import dataclass
from .geometry_types import Point2D, Vec2D


@dataclass
class Panning:
    """Track panning state."""
    end:                    Point2D = Point2D(0, 0)     # Dummy initial value

    def __post_init__(self) -> None:
        self.start = self.end                           # Zero-out the panning vector

    @property
    def vector(self) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=self.start, end=self.end)
