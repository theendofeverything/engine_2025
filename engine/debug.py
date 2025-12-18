"""Debug messages in the HUD and debug artwork."""
from dataclasses import dataclass, field
from .drawing_shapes import Line2D


@dataclass
class DebugArt:
    """Debug Artwork."""
    lines:      list[Line2D] = field(default_factory=list)  # Draw every iteration to persist
    snapshots:  list[Line2D] = field(default_factory=list)  # Sticks around until manually cleared
    is_visible: bool = True

    def reset(self) -> None:
        """Clear the debug art."""
        self.lines = []

    def reset_snapshots(self) -> None:
        """Clear out the snapshots."""
        self.snapshots = []


@dataclass
class DebugHud:
    """Message to display in the debug HUD.

    Attributes:
        text (str):
            Debug HUD text that is updated on every iteration of the game loop.
        snapshots (str):
            Debug HUD text that is printed once and stays in the HUD forever after.
    """
    text:                   str = ""
    snapshots:              str = ""
    is_visible:             bool = True

    def reset(self) -> None:
        """Clear the text in the debug HUD."""
        self.text = ""

    def print(self, text: str) -> None:
        """Append text to the debug HUD."""
        self.text += text
        self.text += "\n"

    def reset_snapshots(self) -> None:
        """Clear out the snapshots."""
        self.snapshots = ""

    def snapshot(self, text: str) -> None:
        """Take a snapshot of a value to debug."""
        self.snapshots += text
        self.snapshots += "\n"

    def print_snapshots(self) -> None:
        """Print the snapshot dictionary to the debug HUD."""
        self.text += f"{self.snapshots}"


@dataclass
class Debug:
    """Debug messages in the HUD and debug artwork."""
    hud:                    DebugHud = DebugHud()
    art:                    DebugArt = DebugArt()
