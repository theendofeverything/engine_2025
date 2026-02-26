"""Art is comprised of vertices."""
import random
from pygame.color import Color
from .drawing_shapes import Line2D
from .geometry_types import Point2D


class Art:
    """Container for all artwork to render."""
    lines: list[Line2D] = []

    @classmethod
    def reset(cls) -> None:
        """Clear out all artwork."""
        cls.lines = []

    @staticmethod
    def randomize_line(line: Line2D, wiggle: float = 0.01) -> Line2D:
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
                          ),
                      color=line.color
                      )

    @classmethod
    def draw_lines(cls, points: list[Point2D], color: Color) -> None:
        """Draw lines given a list of points."""
        # Draw lines between pairs of points
        for i in range(len(points)-1):
            cls.lines.append(Line2D(points[i], points[i+1], color))
        # Draw line from last point back to first point
        cls.lines.append(Line2D(points[-1], points[0], color))
