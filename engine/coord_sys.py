"""CoordinateSystem is a helper struct to organize Game. It contains all things relating to the
coordinate systems: window_size, GCS width, GCS origin, ...
"""
from dataclasses import dataclass
from .geometry_types import Vec2D, Point2D


@dataclass
class CoordinateSystem:
    """All coordinate-system-related game instance attributes."""
    game:                   'Game'
    window_size:            Vec2D
    gcs_width:              float = 2                   # GCS -1:1 fills screen width

    def __post_init__(self) -> None:
        self.origin_p = self.window_center              # Origin is initially the window center

    @property
    def window_center(self) -> Point2D:
        """Return the center of the window in pixel coordinates."""
        return Point2D(self.window_size.x/2, self.window_size.y/2)

    @property
    def translation(self) -> Vec2D:
        """Return the translation vector: adds mouse pan to origin offset.

        CoordinateSystem.translation updates the panning on the screen when it is used in the
        coordiante transforms: CoordinateTransform.gcs_to_pcs() and CoordinateTransform.pcs_to_gcs()
        """
        return Vec2D(x=self.origin_p.x + self.game.panning.vector.x,
                     y=self.origin_p.y + self.game.panning.vector.y)
