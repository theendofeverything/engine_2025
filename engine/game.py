"""Top-level game code.

Abbreviations:
    GCS: Game Coordinate System
    PCS: Pixel Coordinate System
    xfm: transform
"""
from dataclasses import dataclass, field
import logging
import pygame
from .debug import Debug
from .timing import Timing
from .art import Art
from .ui import UI
from .panning import Panning
from .coord_sys import CoordinateSystem
# from .coord_xfm import CoordinateTransform
from .renderer import Renderer
from .geometry_types import Point2D, Vec2D
from .drawing_shapes import Cross


@dataclass
class Game:
    """Game data is shared by all the code"""
    # Instance variables defined in the implicit __init__()
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    ui:         UI = field(init=False)                      # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)        # Track state of PCS and GCS
    # coord_xfm:  CoordinateTransform = field(init=False)     # Xfm vectors btwn PCS and GCS
    renderer:   Renderer = field(init=False)

    def __post_init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        # Handle all user interface events in ui.py (keyboard, mouse, panning, zoom)
        self.ui = UI(game=self, panning=Panning())
        # Set the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                panning=self.ui.panning,
                window_size=Vec2D(x=60*16, y=60*9))
        # Create 'coord_xfm' for transforming between coordinate systems
        # self.coord_xfm = CoordinateTransform(coord_sys=self.coord_sys)
        # Handle rendering in renderer.py
        self.renderer = Renderer(
                game=self,
                window_surface=pygame.display.set_mode(  # Get a window from the OS
                    size=self.coord_sys.window_size.as_tuple(),
                    flags=pygame.RESIZABLE
                    ))

    def run(self, log: logging.Logger) -> None:
        """Run the game."""
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        self.debug.hud.reset()                          # Clear the debug HUD
        self.debug.art.reset()                          # Clear the debug artwork
        self.debug_values()                             # HUD: display values to debug
        self.ui.handle_events(log)                      # Handle all user events
        self.art.reset()                                # Reset previous artwork
        self.draw_a_cross()                             # Draw application artwork
        self.draw_debug_crosses()                       # Draw debug artwork
        self.renderer.render_all()                      # Render all artwork and HUD
        # Delay to keep game at 60 FPS.
        self.timing.ms_per_frame = self.timing.clock.tick(60)

    def debug_values(self) -> None:
        """Most of the values to display in the HUD are printed in this function."""

        def debug_fps() -> None:
            """Display frame duration in milliseconds and rate in FPS."""
            # # TODO: update fps every N frames instead of every frame
            # fps = 1000 / self.timing.ms_per_frame
            # # Use get_fps() for now -- it averages every 10 frames
            fps = self.timing.clock.get_fps()
            self.debug.hud.print(f"frame: {self.timing.ms_per_frame:d}ms ({fps:0.1f}FPS)")

        def debug_window_size() -> None:
            """Display window size."""
            center = (self.coord_sys.window_size.x/2, self.coord_sys.window_size.y/2)
            self.debug.hud.print(f"Window size: {self.coord_sys.window_size}, Center: {center} PCS")

        def debug_mouse_position() -> None:
            """Display mouse position in GCS and PCS."""
            # Get mouse position in pixel coordinates
            mouse_position_tuple = pygame.mouse.get_pos()
            mouse_position = Vec2D(x=mouse_position_tuple[0],
                                   y=mouse_position_tuple[1])
            # Get mouse position in game coordinates
            mouse_g = self.coord_sys.xfm(mouse_position, self.coord_sys.mat.pcs_to_gcs)
            # Test transform by converting back to pixel coordinates
            mouse_p = self.coord_sys.xfm(mouse_g, self.coord_sys.mat.gcs_to_pcs)
            self.debug.hud.print(f"Mouse: {mouse_g.fmt(0.2)}, GCS, {mouse_p.fmt(0.0)}, PCS")

        def debug_mouse_buttons() -> None:
            """Display mouse button state."""
            self.debug.hud.print("Mouse buttons: "
                                 f"1: {self.ui.mouse_button_1}, "
                                 f"2: {self.ui.mouse_button_2}"
                                 )

        def debug_pan() -> None:
            """Display panning values."""
            self.debug.hud.print(f"origin: {self.coord_sys.pcs_origin.fmt(0.2)}, "
                                 f"translation: {self.coord_sys.translation.fmt(0.2)}\n"
                                 f"Panning start: {self.ui.panning.start}, "
                                 f"end: {self.ui.panning.end}, "
                                 f"vector: {self.ui.panning.vector}"
                                 )

        def debug_overlay_is_visible() -> None:
            """Display whether debug artwork overlay is visible."""
            self.debug.hud.print(f"Debug art overlay: {self.debug.art.is_visible}")

        debug_fps()
        debug_window_size()
        debug_mouse_position()
        debug_mouse_buttons()
        debug_pan()
        debug_overlay_is_visible()

    def draw_a_cross(self) -> None:
        """Draw a cross in the GCS."""
        # Create artwork that uses lines
        crosses: list[Cross] = [
            Cross(origin=Point2D(-0.1, 0.1), size=0.2, rotate45=True)
            ]
        # Append line artwork to art.lines
        for cross in crosses:
            for line in cross.lines:
                self.art.lines.append(line)

    def draw_debug_crosses(self) -> None:
        """Draw two crosses in the GCS to help me debug zooming about a point."""
        # Create debug artwork that uses lines
        crosses: list[Cross] = [
            Cross(origin=Point2D(0, 0), size=0.1),
            Cross(origin=Point2D(0.5, 0.5), size=0.1, rotate45=True)
            ]
        # Copy the line artwork to debug.art.lines
        for cross in crosses:
            for line in cross.lines:
                self.debug.art.lines.append(line)
