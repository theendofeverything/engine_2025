"""Art is comprised of vertices."""
from dataclasses import dataclass, field
import random
from .drawing_shapes import Line2D
from .geometry_types import Point2D


@dataclass
class Art:
    """Container for all artwork to render."""
    lines: list[Line2D] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear out all artwork."""
        self.lines = []

    def randomize_line(self, line: Line2D, wiggle: float = 0.01) -> Line2D:
        """Randomize the start and end points of the line by 'wiggle'.

        wiggle (float):
            A value between 0 and 0.1
        """
        return Line2D(start=Point2D(
                          line.start.x + random.uniform(-1*wiggle, wiggle),
                          line.start.y + random.uniform(-1*wiggle, wiggle)
                          ),
                      end=Point2D(
                          line.end.x + random.uniform(-1*wiggle, wiggle),
                          line.end.y + random.uniform(-1*wiggle, wiggle)
                          )
                      )

    def draw_lines(self, points: list[Point2D]) -> None:
        """Draw lines given a list of points."""
        # Draw lines between pairs of points
        for i in range(len(points)-1):
            self.lines.append(Line2D(points[i], points[i+1]))
        # Draw line from last point back to first point
        self.lines.append(Line2D(points[-1], points[0]))
