"""Panning is a helper struct to organize Game. It tracks the mouse panning state.
"""
from dataclasses import dataclass
from .geometry_types import Point2D, Vec2D


@dataclass
class Panning:
    """Track mouse panning state.

    Attributes:
        is_active (bool):
            Panning is in two states: either active (is_active=True) or inactive (is_active=False).
        start (Point2D):
            Position in the pixel coordinate system when panning transitioned to the active state.
            While in the active state, 'start' does not change.
        end (Point2D):
            Latest mouse position in the pixel coordinate system while panning: the game loads 'end'
            with the mouse position on every iteration of the game loop.
        vector (Vec2D):
            Amount of mouse pan, obtained from end - start.
            The 'panning.vector' is picked up during rendering: when the game loop renders drawing
            entities, it converts entity coordinates from the game to the pixel coordinate system.
            That coordinate transform ('xfm.gcs_to_pcs()') uses the origin offset (the
            'coord_sys.translation' vector), which uses the 'panning.vector' in its calculation.

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
