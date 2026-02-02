"""User interface events.

TODO: finish writing this docstring
Events:
    Window resized:
        See 'handle_windowsizechanged_events()'.
        Also see pygame documentation for 'pygame.event'.
    Key pressed:
        See 'handle_keydown_events()'.
    Mouse button down/up:
        See 'handle_mousebutton_down_events()'.
        See 'handle_mousebutton_up_events()'.

User actions:
    Panning:
        See 'handle_mousebutton_down_events()' and 'start_panning()'.
        See 'handle_mousebutton_up_events()' and 'stop_panning()'.
    Zoom:
        See 'handle_mousewheel_events()', 'zoom_out()', and 'zoom_in()'.
    Press 'q': Quit.
    Press 'c': Clear debug snapshot artwork.
    Press 'Space': Toggle debug art overlay.
    Press 'd': Toggle debug HUD.
    Press Ctrl_+: Increase debug HUD font.
    Press Ctrl_-: Decrease debug HUD font.
"""
import sys                  # Exit with sys.exit()
import pathlib
import logging
from dataclasses import dataclass, field
from typing import Callable
import pygame
from .geometry_types import Vec2D, Point2D, DirectedLineSeg2D
from .panning import Panning
from .drawing_shapes import Line2D
from .colors import Colors

FILE = pathlib.Path(__file__).name


@dataclass
class UIMouse:
    """Track mouse button state."""
    button_1: bool = False                              # Track mouse button 1 down/up
    button_2: bool = False                              # Track mouse button 2 down/up


@dataclass
class UI:
    """Handle user interface events.

    Some events, like pygame.QUIT, are handled by UI. But most events are published to whatever
    callbacks the Game registered with UI (via UI.subscribe()). "Publishing an event" just means the
    callback is called with two arguments: the event (pygame.event.Event) and the key modifiers (a
    bitfield of flags like pygame.KMOD_SHIFT).
    """
    game:           "Game"
    panning:        Panning                             # Track panning state
    mouse:          UIMouse = UIMouse()                 # Track mouse button down/up
    subscribers:    list[Callable[[pygame.event.Event, int], None]] = field(default_factory=list)

    def handle_events(self, log: logging.Logger) -> None:
        """Handle events."""
        self.consume_event_queue(log)
        self.update_panning()

    def update_panning(self) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game view on the screen:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- panning.vector

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.start
        """
        panning = self.panning

        if panning.is_active:
            mouse_pos = pygame.mouse.get_pos()
            panning.end = Point2D.from_tuple(mouse_pos)

    def consume_event_queue(self, log: logging.Logger) -> None:
        """Consume all events on the event queue.

        All events are logged, including unused events.
        """
        kmod = pygame.key.get_mods()
        for event in pygame.event.get():
            # Handle event on the engine side
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.WINDOWSIZECHANGED: self.handle_windowsizechanged_events(event, log)
                case pygame.MOUSEBUTTONDOWN: self.handle_mousebutton_down_events(event, kmod, log)
                case pygame.MOUSEBUTTONUP: self.handle_mousebutton_up_events(event, kmod, log)
                case pygame.MOUSEWHEEL: self.handle_mousewheel_events(event, log)
                case _: self.log_unused_events(event, log)
            # Let UI subscribers handle the event
            # NOTE: kmod is stale. Call get_mods() when publishing.
            # self.publish(event, kmod)
            self.publish(event, pygame.key.get_mods())

        if self.mouse.button_1:
            if kmod & pygame.KMOD_SHIFT:
                game = self.game
                # Get mouse position in game coordinates
                mouse_p = Point2D.from_tuple(pygame.mouse.get_pos())
                mouse_g = game.coord_sys.xfm(
                        mouse_p.as_vec(),
                        game.coord_sys.matrix.pcs_to_gcs
                        ).as_point()
                player_to_mouse = DirectedLineSeg2D(
                        start=game.entities["player"].origin,
                        end=mouse_g)
                # Teleport NPC2 to mouse
                game.entities["cross2"].origin = player_to_mouse.parametric_point(1.0)
                # Teleport NPC1 to half-way between player and NPC2
                game.entities["cross1"].origin = player_to_mouse.parametric_point(0.5)

    def subscribe(self, callback: Callable[[pygame.event.Event, int], None]) -> None:
        """Call ui.subscribe(callback) to register "callback" for receiving UI events."""
        self.subscribers.append(callback)

    def publish(self, event: pygame.event.Event, kmod: int) -> None:
        """Publish the event to subscribers by calling all registered callbacks."""
        for subscriber in self.subscribers:
            subscriber(event, kmod)

    def handle_windowsizechanged_events(self,
                                        event: pygame.event.Event,
                                        log: logging.Logger) -> None:
        """User resized the window. Update origin and window size."""
        game = self.game
        # Store the current PCS location of the window center.
        old_window_center = game.coord_sys.window_center
        # Update window_size to the new size.
        game.coord_sys.window_size = Vec2D(x=event.x, y=event.y)
        # Get the vector that goes from the old window center to the new window center.
        translation = Vec2D.from_points(start=old_window_center, end=game.coord_sys.window_center)
        # Use the vector to translate the origin.
        game.coord_sys.pcs_origin.x += translation.x
        game.coord_sys.pcs_origin.y += translation.y
        log.debug(f"Event WINDOWSIZECHANGED, new size: ({event.x}, {event.y})")
        log.debug(f"... game.renderer.window.size: {game.renderer.window.size}")
        # NOTE: from pygame-ce docs:
        # Don't use window.get_surface() when using hardware rendering
        log.debug(f"... game.renderer.window_surface.get_size(): "
                  f"{game.renderer.window_surface.get_size()}")

    def handle_mousewheel_events(self,
                                 event: pygame.event.Event,
                                 log: logging.Logger) -> None:
        """Handle mousewheel events."""
        match event.y:
            case -1:
                log.debug("ZOOM OUT")
                self.zoom_out()
            case 1:
                log.debug("ZOOM IN")
                self.zoom_in()
            case _:
                log.debug("Unexpected y-value")
        log.debug(f"Event MOUSEWHEEL, flipped: {event.flipped}, "
                  f"x:{event.x}, y:{event.y}, "
                  f"precise_x:{event.precise_x}, precise_y:{event.precise_y}")

    def handle_mousebutton_down_events(self,
                                       event: pygame.event.Event,
                                       kmod: int,
                                       log: logging.Logger) -> None:
        """Handle event mouse button down."""
        log.debug("Event MOUSEBUTTONDOWN, "
                  f"pos: {event.pos}, ({type(event.pos[0])})"
                  f"button: {event.button}")
        match event.button:
            case 1:
                self.mouse.button_1 = True              # Left mouse button pressed
                if kmod & pygame.KMOD_CTRL:
                    self.start_panning(event.pos)           # Start panning
            case 2:
                self.mouse.button_2 = True              # Middle mouse button pressed
                self.start_panning(event.pos)           # Start panning
            case _:
                pass

    def handle_mousebutton_up_events(self,
                                     event: pygame.event.Event,
                                     kmod: int,
                                     log: logging.Logger) -> None:
        """Handle event mouse button up."""
        log.debug("Event MOUSEBUTTONUP, "
                  f"pos: {event.pos}, "
                  f"button: {event.button}")
        match event.button:
            case 1:
                self.mouse.button_1 = False             # Left mouse button released
                if kmod & pygame.KMOD_CTRL:
                    self.stop_panning()                     # Stop panning
            case 2:
                self.mouse.button_2 = False             # Middle mouse button released
                self.stop_panning()                     # Stop panning
            case _:
                pass

    def log_unused_events(self, event: pygame.event.Event, log: logging.Logger) -> None:
        """Log events that I have not found a use for yet."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                log.debug(f"Event MOUSEBUTTONDOWN, pos: {event.pos}, button: {event.button}")
            case pygame.MOUSEBUTTONUP:
                log.debug(f"Event MOUSEBUTTONUP, pos: {event.pos}, button: {event.button}")
            case pygame.VIDEORESIZE:
                # Do we need this?
                log.debug(f"Event VIDEORESIZE, new size: ({event.w}, {event.h})")
            case pygame.WINDOWRESIZED:
                # Do we need this?
                log.debug(f"Event WINDOWRESIZED, new size: ({event.x}, {event.y})")
            case _: log.debug(event)

    def _zoom(self, scale: float) -> None:
        """Private zoom function used by zoom_in() and zoom_out().

        Zoom about a point: use mouse position to create an offset in GCS units before and after the
        zoom. Use the new zoom scale to convert the offset vector back to PCS units. Add the offset
        vector to the PCS origin. Be careful of the minus sign!
        """
        game = self.game
        debug = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_p = Point2D.from_tuple(mouse_pos)
        # Mark the original mouse location in GCS
        mouse_g_end = game.coord_sys.xfm(
                mouse_p.as_vec(),
                game.coord_sys.matrix.pcs_to_gcs
                ).as_point()

        # Update the coordinate system zoom scale
        game.coord_sys.gcs_width *= scale

        # Mark the new location in GCS
        mouse_g_start = game.coord_sys.xfm(
                mouse_p.as_vec(),
                game.coord_sys.matrix.pcs_to_gcs
                ).as_point()
        # Create an offset vector to get the mouse back to the original location
        if debug:
            game.debug.art.snapshot(Line2D(start=mouse_g_start, end=mouse_g_end,
                                           color=Colors.panning))
            game.debug.snapshots["zoom_about"] = ("UI -> _zoom() | zoom about "
                                                  f"starts: {mouse_g_start}, "
                                                  f"ends: {mouse_g_end}")

        offset_g = Vec2D.from_points(start=mouse_g_start, end=mouse_g_end)
        if debug:
            game.debug.snapshots["offset_g"] = f"UI -> _zoom() | offset_g: {offset_g}GCS"
        # Scale the vector from GCS to PCS
        offset_p = Vec2D(x=game.coord_sys.scaling.gcs_to_pcs*offset_g.x,
                         y=game.coord_sys.scaling.gcs_to_pcs*offset_g.y)
        # Note: although this is in PCS, the offset is fractional: (float, float)
        if debug:
            game.debug.snapshots["offset_p"] = f"UI -> _zoom() | offset_p: {offset_p}GCS"
        # Change the PCS origin to move the GCS origin by that offset (keep zoom about the mouse)
        # I don't understand why I have to subtract the x-offset, but this is what works.
        game.coord_sys.pcs_origin.x -= offset_p.x
        game.coord_sys.pcs_origin.y += offset_p.y

    def zoom_out(self) -> None:
        """Zoom out."""
        self._zoom(scale=1.1)

    def zoom_in(self) -> None:
        """Zoom in."""
        self._zoom(scale=0.9)

    def start_panning(self, position: tuple[int | float, int | float]) -> None:
        """User started panning."""
        self.panning.is_active = True
        self.panning.start = Point2D.from_tuple(position)

    def stop_panning(self) -> None:
        """User stopped panning."""
        game = self.game
        self.panning.is_active = False
        game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
        self.panning.start = self.panning.end  # Zero-out the panning vector
