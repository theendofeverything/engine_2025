#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Game kata 2025-11-17

* [x] Fill the screen with a color
    * This required that I:
        * store the Surface returned by pygame.display.set_mode in the Game
        * pass the Game to loop()
* [x] Draw something on the screen
    * I drew a line using pygame.draw.line()
* [x] Replace pygame.color.Color() with named colors:
    * Create a library of named colors: Colors.name1, Colors.name2, etc.
* [x] Render some text
* [x] Render mouse position
    [x] Create shortcut ;kpg to open local copy of pygame docs in browser
* [x] Render FPS and milliseconds per frame
* [x] Track window size
    * [x] Handle window resize events
    * [x] Capture new window size
* [x] Track mouse zoom
    * [x] Zoom at a point: calculate a translation vector based on the location of the zoom. Get the
    mouse location, convert to GCS, then after the zoom increment, convert the mouse coordinate to
    GCS again. Use the two GCS points to get a vector. Convert that vector to pixel coordinates
    (this was tricky to figure out), then offset the PCS origin by that vector so that the screen
    pans just the right amount to keep that mouse position at the center.
* [x] Track mouse pan
    * [x] Catch events for mouse button press and release
    * [x] Track whether mouse button 1 is up/down
    * [x] Track where pan starts and ends
    * [x] Calculate the panning vector
    * [x] Define translation and panning vectors as properties (values returned by function)
    * [x] Update the origin when panning ends
    * [x] Update the origin when screen is resized
* [x] Replace pixel coordinates with world space coordinates
    * [x] Create high-school algebra transforms to map from world space to
          pixel space
    * [x] Draw in GCS then render in PCS
    * [x] Eliminate hard-coded values in the transforms
        * [x] Hard-coded scaling factor screen_width/2 becomes screen_width/gcs_width
              where gcs_width is adjusted on mouse zoom
        * [x] Hard-coded translation screen_xy/2 must get updated on zoom and on pan
    * [x] Create matrix algebra transforms
        * [x] Create gcs_to_pcs
        * [x] Document this
        * [x] Calculate matrix inverse of a 2x2 augmented with homogeneous coordinates
* [x] Calculate matrix inverse of a general 3x3
* [x] Make 'engine' reusable with any 'game':
    * Pull 'engine/game.py' out of `engine/` and up one level
    * Leave `main.py` as-is (it launches game but is not specific to any game)
    * Intent is to use `game.py` as a starting point in writing games.
* [ ] Simplify debug HUD variable snapshots
* [ ] Provide ability to color debug HUD text to make it easier to notice special values.
* [ ] Put a transparent background behind the debug hud so that it is easier to read.
"""

from dataclasses import dataclass, field
import logging
import pygame
from engine.debug import Debug
from engine.timing import Timing
from engine.art import Art
from engine.ui import UI
from engine.panning import Panning
from engine.coord_sys import CoordinateSystem
from engine.renderer import Renderer
from engine.geometry_types import Point2D, Vec2D
from engine.drawing_shapes import Cross
from engine.colors import Colors


@dataclass
class Game:
    """Top-level game code.

    Game data is shared by all the code.

    Abbreviations:
        GCS: Game Coordinate System
        PCS: Pixel Coordinate System
        xfm: transform

    Suffix abbreviations:
        h:  homogeneous coordinates
        _g: GCS
        _p: PCS

    Game code is divided up as follows:
    >>> game = Game()
    >>> game
    Game(debug=Debug(...),
         timing=Timing(...),
         art=Art(...),
         renderer=Renderer(...),
         ui=UI(...),
         coord_sys=CoordinateSystem(...))
    """
    # Instance variables defined in the implicit __init__()
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    renderer:   Renderer = field(init=False)
    ui:         UI = field(init=False)                      # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)        # Track state of PCS and GCS

    def __post_init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        self.debug_font = "fonts/ProggyClean.ttf"

        # Set the window size
        window_size = (60*16, 60*9)

        # Handle rendering in renderer.py
        # Note: The window size is just an initial value.
        #   On WINDOWSIZECHANGED events, the window size and the display surface size will
        #   automatically adjust to the new size value. It is not necessary to create a new
        #   window_surface with the new window size. See handle_windowsizechanged_events.
        self.renderer = Renderer(
                game=self,
                window_surface=pygame.display.set_mode(  # Get a window from the OS
                    size=window_size,
                    flags=pygame.RESIZABLE
                    ))

        # Handle all user interface events in ui.py (keyboard, mouse, panning, zoom)
        self.ui = UI(game=self, panning=Panning())

        # Set the GCS to fit the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                window_size=Vec2D.from_tuple(window_size),
                panning=self.ui.panning)

    def run(self, log: logging.Logger) -> None:
        """Run the game."""
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        # Update debug
        self.debug.hud.reset()                          # Clear the debug HUD
        self.debug_top_values()                         # Load debug HUD with top values
        self.reset_art()                                # Clear old art
        self.ui.handle_events(log)                      # Handle all user events
        self.update_animations()                        # Advance animation ticks
        self.draw_remaining_art()                       # Draw any remaining art not already drawn
        self.debug.display_snapshots_in_hud()           # Print snapshots in HUD last
        self.renderer.render_all()                      # Render all art and HUD
        self.timing.maintain_framerate(fps=60)          # Run at 60 FPS

    def update_animations(self) -> None:
        """Update animations based on the frame count."""
        hud = self.debug.hud
        timing = self.timing
        if not timing.is_paused:
            timing.ticks.update()
        hud.print("|\n+- loop() -> update_animations()")
        hud.print(f"| +- frames: {timing.ticks.frames}")
        hud.print(f"| +- {timing.ticks.t1}")

    def reset_art(self) -> None:
        """Clear out old artwork: application and debug."""
        self.art.reset()                                # Reset application artwork
        self.debug.art.reset()                          # Clear the debug artwork

    def draw_remaining_art(self) -> None:
        """Update art and debug art"""
        self.draw_a_cross()                             # Draw application artwork
        self.draw_debug_crosses()                       # Draw debug artwork

    def debug_top_values(self) -> None:
        """Most of the values to display in the HUD are printed in this function."""

        debug = self.debug
        debug.hud.print(f"{'debug_top_values()':<60} {'debug.hud.font_size:':<22}"
                        f"{debug.hud.font_size.value}")
        debug.hud.print(f"{'|':<60} {'debug.art.is_visible:':<22}"
                        f"{debug.art.is_visible} ('d' to toggle)")

        def debug_fps() -> None:
            """Display frame duration in milliseconds and rate in FPS."""
            timing = self.timing
            # # Old: use get_fps() -- it averages every 10 frames
            # fps = timing.clock.get_fps()
            if timing.ticks.hud_fps.is_period:
                # Update buffered milliseconds per frame once every period (30 frames).
                # See Ticks.hud_fps and Ticks.update() for period.
                timing.update_buffered_ms_per_frame()
            # Print buffered versions to HUD
            fps = timing.fps_buffered
            ms_per_frame = timing.ms_per_frame_buffered
            debug.hud.print(f"|\n+- FPS: {fps:0.1f}, frame period: {ms_per_frame:d}ms")

        def debug_window_size() -> None:
            """Display window size."""
            debug.hud.print("|\n+- OS window (in pixels)")
            debug.hud.print(f"|  +- window_size: {self.coord_sys.window_size.fmt(0.0)}")
            debug.hud.print(f"|  +- window_center: {self.coord_sys.window_center.fmt(0.0)}")

        debug_fps()
        debug_window_size()
        debug.hud.print("\nLocals")                     # Local debug prints (e.g., from UI)

    def draw_a_cross(self) -> None:
        """Draw a cross in the GCS."""
        # Create artwork that uses lines
        crosses: list[Cross] = [
            Cross(origin=Point2D(-0.1, 0.1), size=0.2, rotate45=True, color=Colors.line)
            ]
        # Append line artwork to art.lines
        for cross in crosses:
            for line in cross.lines:
                self.art.lines.append(line)

    def draw_debug_crosses(self) -> None:
        """Draw two crosses in the GCS to help me debug zooming about a point."""
        # Create debug artwork that uses lines
        crosses: list[Cross] = [
            Cross(origin=Point2D(0, 0), size=0.1, color=Colors.line_debug),
            Cross(origin=Point2D(0.5, 0.5), size=0.1, rotate45=True, color=Colors.line_debug)
            ]
        # Copy the line artwork to debug.art.lines
        for cross in crosses:
            for line in cross.lines:
                self.debug.art.lines_gcs.append(line)
