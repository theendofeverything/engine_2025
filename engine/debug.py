"""Debug messages in the HUD and debug artwork."""
from dataclasses import dataclass, field
from .drawing_shapes import Line2D


@dataclass
class FontSize:
    """Font size of pgyame.font.Sysfont()."""
    value: int
    minimum: int
    maximum: int

    def increase(self) -> None:
        """Increase the font size. Clamp at maximum size."""
        self.value += 1
        self.value = min(self.value, self.maximum)

    def decrease(self) -> None:
        """Decrease the font size. Clamp at minimum size."""
        self.value -= 1
        self.value = max(self.value, self.minimum)


@dataclass
class DebugArt:
    """Debug Artwork.

    Attributes:
        is_visible (str):
            Controls whether debug artwork should be visible.
            The renderer checks this to see whether to render debug artwork.
            Debug artwork visibility is toggled in the ui.
            Intended usage:
                On user event to toggle debug artwork:
                    game.debug.art.is_visible = not game.debug.art.is_visible
                In renderer:
                    if game.debug.art.is_visible:
                        render_gcs_lines(lines=game.debug.art.lines_gcs, ...
                        render_pcs_lines(lines=game.debug.art.lines_pcs, ...
        lines_gcs (list[Line2D]):
            A list of debug lines to draw.
            The lines are in the GCS. The renderer converts the coordinates to PCS in render_shapes.
            Use debug.art.reset() to clear 'lines' to an empty list.
            Intended usage:
                Create some_shape. Then add the lines in this shape to the debug artwork:
                    for line in some_shape.lines:
                        debug.art.lines_gcs.append(line)
                The renderer draws these to the window in render_shapes:
                    if game.debug.art.is_visible:
                        render_lines(lines=game.debug.art.lines, ...
                The debug artwork is reset at the top of the game loop:
                    self.debug.art.reset()
        lines_pcs (list[Line2D]):
            A list of debug lines to draw.
            The lines are in the PCS. Same idea as lines_gcs, but the renderer does not have to
            convert coordinates to PCS.
        snapshots (list[Line2D]):
            Debug lines that persist until manually cleared.
            The lines are in the GCS. The renderer converts the coordinates to PCS in render_shapes.
            Use debug.art.reset_snapshots() to reset 'snapshots' to an empty list.
            Intended usage:
                Use 'debug.art.snapshot()' to append a debug line art in event-triggered code:
                    if debug:
                        game.debug.art.snapshot(Line2D(start=mouse_g_start, end=mouse_g_end))
                Use 'debug.art.reset_snapshots()' at start of code block to clear old line art.
                    if debug:
                        game.debug.hud.reset_snapshots()
                The renderer draws these to the window in render_shapes:
                    if game.debug.art.is_visible:
                        render_lines(lines=game.debug.art.snapshots, ...
    """
    is_visible: bool = True  # Controls whether debug artwork is visible
    lines_gcs:  list[Line2D] = field(default_factory=list)  # Cleared on each iteration of game loop
    lines_pcs:  list[Line2D] = field(default_factory=list)  # Cleared on each iteration of game loop
    snapshots:  list[Line2D] = field(default_factory=list)  # Sticks around until manually cleared

    def reset(self) -> None:
        """Clear the debug art."""
        self.lines_gcs = []
        self.lines_pcs = []

    def reset_snapshots(self) -> None:
        """Clear out the snapshots."""
        self.snapshots = []

    def snapshot(self, line: Line2D) -> None:
        """Append line to snapshots."""
        self.snapshots.append(line)


@dataclass
class DebugHud:
    """Messages to display in the debug HUD.

    Attributes:
        is_visible (bool):
            Control whether HUD should be visible or not.
            The renderer checks this to see whether to render the HUD.
            HUD visibility is toggled in the ui.
            Intended usage:
                On user event to toggle HUD:
                    game.debug.hud.is_visible = not game.debug.hud.is_visible
                In renderer:
                    if game.debug.hud.is_visible:
                        self.render_debug_hud()
        font_size (FontSize):
            Control HUD font size with Ctrl_+/-.
            Font size is initialized to 16. Minimum is 6, maximum is 30.
            Intended usage:
                The ui adjusts font size on keydown events:
                    case pygame.K_EQUALS:
                        if kmod & (pygame.KMOD_CTRL | pygame.KMOD_SHIFT):
                            game.debug.hud.font_size.increase()
                    case pygame.K_MINUS:
                        if kmod & (pygame.KMOD_CTRL):
                            game.debug.hud.font_size.decrease()
                The renderer uses font size to create the font when rendering the HUD:
                    font = pygame.font.SysFont("RobotoMono", game.debug.hud.font_size.value, ...
        _text (str):
            The text that is displayed in the Debug HUD.
            Don't manipulate '_text' directly.
            Use debug.hud.print() to append text to '_text'. This also appends a newline.
            Use debug.hud.reset() to clear '_text' to an empty string.
            Use debug.hud.lines to access '_text' as a list of lines of text.
            Intended usage:
                Use 'debug.hud.print()' to debug values updated on every iteration of the game loop.
                At the top of the game loop, use 'debug.hud.reset()' to clear '_text'.
                The renderer uses 'debug.hud.lines' to iterate over the lines of text in '_text'.
        _snapshots (str):
            Debug HUD text that persists until manually cleared.
            Don't manipulate '_snapshots' directly.
            Use debug.hud.snapshot() to append text to '_snapshots'.
            Use debug.hud.reset_snapshots() to reset '_snapshots' to an empty string.
            Intended usage:
                Use 'debug.hud.snapshot()' to debug values in event-triggered code.
                Use 'debug.hud.reset_snapshots()' at the top of the code block to clear old values.
    """
    is_visible: bool = True     # Control whether HUD should be visible or not.
    font_size:  FontSize = FontSize(value=16, minimum=6, maximum=30)  # Track HUD font size
    _text:      str = ""        # The text that is displayed in the Debug HUD.
    _snapshots: str = ""        # Debug HUD text that persists until manually cleared.

    @property
    def lines(self) -> list[str]:
        """Return _text as a list of lines."""
        return self._text.split("\n")

    def print(self, text: str) -> None:
        """Append text to the debug HUD."""
        self._text += text
        self._text += "\n"

    def reset(self) -> None:
        """Clear the text in the debug HUD."""
        self._text = ""

    def snapshot(self, text: str) -> None:
        """Take a snapshot of a value to debug."""
        self._snapshots += text
        self._snapshots += "\n"

    def print_snapshots(self) -> None:
        """Print the snapshot dictionary to the debug HUD."""
        self._text += f"{self._snapshots}"

    def reset_snapshots(self) -> None:
        """Clear out the snapshots."""
        self._snapshots = ""


@dataclass
class Debug:
    """Debug messages in the HUD and debug artwork."""
    hud:                    DebugHud = DebugHud()
    art:                    DebugArt = DebugArt()
