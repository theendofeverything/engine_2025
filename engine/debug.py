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
                        game.debug.art.reset_snapshots()
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
    """
    font_size:  FontSize = FontSize(value=16, minimum=6, maximum=30)  # Track HUD font size
    is_visible: bool = True     # Control whether HUD should be visible or not.
    _text:      str = ""        # The text that is displayed in the Debug HUD.
    # Connect variables to user input from HUD
    controls:   dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.define_controls()

    def define_controls(self) -> None:
        """Define variables that connect to user input from the HUD."""
        self.controls["k"] = 0.04
        self.controls["b"] = 0.064

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


@dataclass
class Debug:
    """Debug messages in the HUD and debug artwork."""
    hud:                    DebugHud = DebugHud()
    art:                    DebugArt = DebugArt()
    snapshots:              dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        self.snapshots = {}

    def display_snapshots_in_hud(self) -> None:
        """Display variable snapshots in the HUD.

        Variable snapshots are for displaying variables in the HUD for code that doesn't run on
        every iteration of the game loop.

        Usage:

            The application code just takes a snapshot by writing to dict 'debug.snapshots':

                def _zoom(self, scale: float) -> None:
                    debug = True
                    ...
                    if debug:
                        game.debug.snapshots["zoom_about"] = ("UI -> _zoom() | zoom about "
                                                              f"starts: {mouse_g_start}, "
                                                              f"ends: {mouse_g_end}")

            And the variable will be printed to the HUD whenever the application calls
            'debug.display_snapshots_in_hud()':

                def loop():
                    debug.hud.reset()                   # Clear the debug HUD
                    debug_fps()                         # Application debugging func: prints to HUD
                    ...
                    debug.display_snapshots_in_hud()    # THIS FUNC: prints all snapshots to HUD

        The HUD displays snapshot variables like this:

        Snapshots
        |
        +- UI -> _zoom() | zoom about starts: (-0.06, -0.14), ends: (-0.06, -0.15)
        |
        ...
        """
        snapshots = self.snapshots
        hud = self.hud
        hud.print("\nSnapshots")
        for msg in snapshots.values():
            hud.print(f"|\n+- {msg}")
