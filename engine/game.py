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
from .coord_xfm import CoordinateTransform
from .renderer import Renderer
from .geometry_types import Point2D, Vec2D
from .drawing_shapes import Line2D, Cross


@dataclass
class Game:
    """Game data is shared by all the code"""
    # Instance variables defined in the implicit __init__()
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    ui:         UI = field(init=False)                  # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)    # PCS and GCS
    coord_xfm:  CoordinateTransform = field(init=False)
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
        self.coord_xfm = CoordinateTransform(coord_sys=self.coord_sys)
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
