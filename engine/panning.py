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
            The 'panning.vector' is picked up during rendering, as follows:
                When the game loop renders drawing entities, it converts entity coordinates from
                GCS to PCS:
                    coord_sys.xfm(v:Vec2D, coord_sys.mat.gcs_to_pcs)
                That coordinate transform matrix is calculated using the origin offset vector:
                    coord_sys.translation
                And coord_sys.translation is calculated using the 'panning.vector' (this attribute).

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
