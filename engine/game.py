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
from .drawing_shapes import Line2D
from .timing import Timing
from .coord_sys import CoordinateSystem
from .renderer import Renderer
from .ui import UI


class Game:
    """Game data is shared by all the code"""
    ui:                     UI
    timing:                 Timing
    coord_sys:              CoordinateSystem
    xfm:                    CoordinateTransform
    renderer:               Renderer

    shapes:                 dict[str, list[Line2D]]

    def __init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
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

    def run(self, log: logging.Logger) -> None:
        """Run the game."""
        self.shapes = {}                                # Shape primitives
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        self.ui.handle_events(log)
        self.draw_shapes()                              # Physics
        self.renderer.render_all()
        # Delay to keep game at 60 FPS.
        self.timing.ms_per_frame = self.timing.clock.tick(60)

    def draw_shapes(self) -> None:
        """Draw shapes in GCS."""
        lines: list[Line2D] = []
        # Append line artwork to lines
        lines.append(
                Line2D(start=Point2D(-0.2, -0.2),
                       end=Point2D(0.2, 0.2)
                       ))
        lines.append(
                Line2D(start=Point2D(0.2, -0.2),
                       end=Point2D(-0.2, 0.2)
                       ))
        # Update shapes dict
        self.shapes['lines'] = lines
