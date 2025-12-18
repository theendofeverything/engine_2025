"""CoordinateSystem is a helper struct to organize Game attributes for the coordinate systems.

There are two coordinate systems:
    PCS: Pixel Coordinate System
    GCS: Game Coordinate System
"""
from dataclasses import dataclass
from .geometry_types import Vec2D, Point2D
from .panning import Panning


@dataclass
class CoordinateSystem:
    """Game attributes for the coordinate systems.

    Attributes:
        window_size (Vec2D):
            The size of the OS window in pixels.
        gcs_width (float):
            The visible width of the game in the game coordinate system.
        pcs_origin (Point2D):
            The game coordinate system origin in pixel coordinates.

    Read-only attributes:
        window_center (Point2D):
            Center of the window in pixel coordinates.
        translation (Vec2D):
            This is a vector in pixel coordinates from the topleft of the window to the game origin,
            i.e., this translation vector describes the origin offset.
            The name 'translation' refers to how it is used in the CoordinateTransform.
            Mouse panning is included in the origin offset when calculating 'translation'.
        scale_gcs_to_pcs (float):
            Scaling factor to transform from units of GCS to PCS.
            The scale is based on the visible width of the GCS at this zoom level
        scale_pcs_to_gcs (float):
            Scaling factor to transform from units of PCS to GCS.
            This is the inverse of scale_gcs_to_pcs.
    """
    panning:                Panning
    window_size:            Vec2D
    gcs_width:              float = 2                   # GCS -1:1 fills screen width

    def __post_init__(self) -> None:
        self.pcs_origin = self.window_center              # Origin is initially the window center

    @property
    def window_center(self) -> Point2D:
        """The center of the window in pixel coordinates."""
        return Point2D(self.window_size.x/2, self.window_size.y/2)

    @property
    def translation(self) -> Vec2D:
        """The translation vector describing the origin offset relative to the window (0,0).

        Dependency chain showing how translation is used and how it is affected by panning:
            renderer <-- xfm.gcs_to_pcs <-- coord_sys.translation <-- panning.vector
            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.start
        """
        return Vec2D(x=self.pcs_origin.x + self.panning.vector.x,
                     y=self.pcs_origin.y + self.panning.vector.y)

    @property
    def scale_gcs_to_pcs(self) -> float:
        """Scaling factor to convert from units of GCS to PCS."""
        return self.window_size.x/self.gcs_width

    @property
    def scale_pcs_to_gcs(self) -> float:
        """Scaling factor to convert from units of PCS to GCS."""
        return 1/(self.scale_gcs_to_pcs)
