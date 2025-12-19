"""Art is comprised of vertices."""
from dataclasses import dataclass, field
from .drawing_shapes import Line2D


@dataclass
class Art:
    """Container for all artwork to render."""
    lines: list[Line2D] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear out all artwork."""
        self.lines = []
