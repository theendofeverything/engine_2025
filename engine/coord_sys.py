"""CoordinateSystem is a helper struct to organize Game. It contains all things relating to the
coordinate systems: window_size, GCS width, GCS origin, ...
"""
from dataclasses import dataclass
from .geometry_types import Vec2D, Point2D


@dataclass
class CoordinateSystem:
    """All coordinate-system-related game instance attributes."""
    window_size:            Vec2D
    gcs_width:              float = 2                   # GCS -1:1 fills screen width

    def __post_init__(self) -> None:
        self.origin_p = self.window_center              # Origin is initially the window center

    @property
    def window_center(self) -> Point2D:
        """Return the center of the window in pixel coordinates."""
        return Point2D(self.window_size.x/2, self.window_size.y/2)
