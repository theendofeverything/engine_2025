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
         ui=UI(...),
         coord_sys=CoordinateSystem(...),
         renderer=Renderer(...))
    """
    # Instance variables defined in the implicit __init__()
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    ui:         UI = field(init=False)                      # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)        # Track state of PCS and GCS
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
            self.debug.hud.print(f"Window size: {self.coord_sys.window_size.fmt(0.0)}, "
                                 f"Center: {self.coord_sys.window_center.fmt(0.0)} PCS")

        def debug_mouse_position() -> None:
            """Display mouse position in GCS and PCS."""
            # Get mouse position in pixel coordinates
            mouse_position = Point2D.from_tuple(pygame.mouse.get_pos())
            # Get mouse position in game coordinates
            mouse_gcs = self.coord_sys.xfm(mouse_position.as_vec(), self.coord_sys.mat.pcs_to_gcs)
            # Test transform by converting back to pixel coordinates
            mouse_pcs = self.coord_sys.xfm(mouse_gcs, self.coord_sys.mat.gcs_to_pcs)
            self.debug.hud.print(f"Mouse: {mouse_gcs}, GCS, {mouse_pcs.fmt(0.0)}, PCS")

        def debug_mouse_buttons() -> None:
            """Display mouse button state."""
            self.debug.hud.print("Mouse buttons: "
                                 f"1: {self.ui.mouse_button_1}, "
                                 f"2: {self.ui.mouse_button_2}"
                                 )

        def debug_pan() -> None:
            """Display panning values."""
            self.debug.hud.print(f"origin: {self.coord_sys.pcs_origin}, "
                                 f"translation: {self.coord_sys.translation}\n"
                                 f"Panning start: {self.ui.panning.start.fmt(0.0)}, "
                                 f"end: {self.ui.panning.end.fmt(0.0)}, "
                                 f"vector: {self.ui.panning.vector.fmt(0.0)}"
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
