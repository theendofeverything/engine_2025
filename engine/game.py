"""Top-level game code.

Abbreviations:
    GCS: Game Coordinate System
    PCS: Pixel Coordinate System
    xfm: transform
"""
import logging
import pygame
from .geometry_types import Point2D, Vec2D
from .geometry_operators import CoordinateTransform
from .drawing_shapes import Line2D, Cross
from .timing import Timing
from .coord_sys import CoordinateSystem
from .renderer import Renderer
from .ui import UI
from .debug import Debug
from .art import Art


class Game:
    """Game data is shared by all the code"""
    debug:                  Debug
    ui:                     UI
    timing:                 Timing
    coord_sys:              CoordinateSystem
    xfm:                    CoordinateTransform
    renderer:               Renderer
    art:                    Art

    def __init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        # Display debug prints in the debug HUD
        self.debug = Debug()
        # Display debug art
        # Handle all user interface events in ui.py
        self.ui = UI(game=self)
        # Set up a clock to set frame rate and measure frame period
        self.timing = Timing()
        # Set the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                panning=self.ui.panning,
                window_size=Vec2D(x=60*16, y=60*9))
        # Create 'xfm' for transforming between coordinate systems
        self.xfm = CoordinateTransform(coord_sys=self.coord_sys)
        # Handle rendering in renderer.py
        self.renderer = Renderer(
                game=self,
                window_surface=pygame.display.set_mode(  # Get a window from the OS
                    size=self.coord_sys.window_size.as_tuple(),
                    flags=pygame.RESIZABLE
                    ))
        # Set up all artwork in art
        self.art = Art()

    def run(self, log: logging.Logger) -> None:
        """Run the game."""
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        self.debug.hud.reset()                          # Clear the debug HUD
        self.debug.art.reset()                          # Clear the debug artwork
        self.debug_fps()                                # Display FPS in the HUD
        self.ui.handle_events(log)                      # Handle all user events
        self.art.reset()                                # Reset previous artwork
        self.draw_shapes()                              # Draw application artwork
        self.draw_debug_shapes()                        # Draw debug artwork
        self.renderer.render_all()                      # Render all artwork and HUD
        # Delay to keep game at 60 FPS.
        self.timing.ms_per_frame = self.timing.clock.tick(60)

    def debug_fps(self) -> None:
        """Display frame duration in milliseconds and rate in FPS."""
        # # TODO: update fps every N frames instead of every frame
        # fps = 1000 / self.timing.ms_per_frame
        # # Use get_fps() for now -- it averages every 10 frames
        fps = self.timing.clock.get_fps()
        self.debug.hud.print(f"frame: {self.timing.ms_per_frame:d}ms ({fps:0.1f}FPS)")

    def draw_shapes(self) -> None:
        """Draw shapes in GCS."""
        # Create artwork that uses lines
        crosses: list[Cross] = [
            Cross(origin=Point2D(-0.1, 0.1), size=0.2, rotate45=True)
            ]
        # Append line artwork to lines
        lines: list[Line2D] = []
        for cross in crosses:
            for line in cross.lines:
                lines.append(line)
        # Update shapes dict with lines
        self.art.shapes["lines"] = lines

    def draw_debug_shapes(self) -> None:
        """Draw debug artwork in GCS."""
        if self.debug.art.is_visible:
            # Create debug artwork that uses lines
            crosses: list[Cross] = [
                Cross(origin=Point2D(0, 0), size=0.1),
                Cross(origin=Point2D(0.5, 0.5), size=0.1, rotate45=True)
                ]
            # Append line artwork to lines
            lines: list[Line2D] = []
            for cross in crosses:
                for line in cross.lines:
                    lines.append(line)
            # Append debug artwork
            for line in self.debug.art.lines:
                lines.append(line)
            # Append debug snapshot art (if any)
            for line in self.debug.art.snapshots:
                lines.append(line)
            # Update shapes dict
            self.art.shapes["lines_debug"] = lines
