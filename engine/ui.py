"""User interface events.

TODO: finish writing this docstring
Events:
    Window resized:
        See 'handle_windowsizechanged_events()'.
        Also see pygame documentation for 'pygame.event'.
    Key pressed:
        See 'ui_callback_to_map_event_to_action()' in 'Game':
            'case pygame.KEYDOWN'
            'case pygame.KEYUP'
            '_handle_keyboard_action_events()'
        See 'InputMapper.key_map'
    Mouse button down/up:
        See 'ui_callback_to_map_event_to_action()' in 'Game':
            'case pygame.MOUSEBUTTONDOWN'
            'case pygame.MOUSEBUTTONUP'
            '_handle_mouse_action_events()'
        See 'InputMapper.mouse_map'

User actions:
    Panning:
        See 'OngoingAction.panning.start()'
        See 'OngoingAction.panning.stop()'
    Zoom:
        See 'handle_mousewheel_events()', 'zoom_out()', and 'zoom_in()'.
    Press 'q': Quit.
    Press 'c': Clear debug snapshot artwork.
    Press 'Space': Toggle debug art overlay.
    Press 'd': Toggle debug HUD.
    Press Ctrl_+: Increase debug HUD font.
    Press Ctrl_-: Decrease debug HUD font.
"""
from __future__ import annotations
import sys                  # Exit with sys.exit()
import pathlib
import logging
from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
import pygame
from .geometry_types import Vec2D, Point2D
from .drawing_shapes import Line2D
from .colors import Colors

FILE = pathlib.Path(__file__).name


@dataclass
class MousePressed:
    """Track mouse button pressed state."""
    left: bool = False  # Track mouse button 1 down/up
    middle: bool = False  # Track mouse button 2 down/up
    right: bool = False  # Track mouse button 3 down/up


class MouseButton(Enum):
    """Enumerate the mouse button values from pygame.Event.button"""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5

    @classmethod
    def from_event(cls, event: pygame.Event) -> MouseButton:
        """Get MouseButton from an event (uses event.button)."""
        return cls(event.button)


@dataclass
class UI:
    """Handle user interface events.

    Some events, like pygame.QUIT, are handled by UI. But most events are published to whatever
    callbacks the Game registered with UI (via UI.subscribe()). "Publishing an event" just means the
    callback is called with two arguments: the event (pygame.event.Event) and the key modifiers (a
    bitfield of flags like pygame.KMOD_SHIFT).
    """
    game: "Game"
    mouse_pressed: MousePressed = MousePressed()  # Track mouse button down/up
    subscribers:    list[Callable[[pygame.event.Event, int], None]] = field(default_factory=list)

    def handle_events(self, log: logging.Logger) -> None:
        """Handle events."""
        self.consume_event_queue(log)
        # self.update_panning()

    def consume_event_queue(self, log: logging.Logger) -> None:
        """Consume all events on the event queue.

        All events are logged, including unused events.
        """
        # kmod = pygame.key.get_mods()
        for event in pygame.event.get():
            # Handle event on the engine side
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.WINDOWSIZECHANGED: self.handle_windowsizechanged_events(event, log)
                case pygame.MOUSEBUTTONDOWN: self.track_mouse_pressed(event, True, log)
                case pygame.MOUSEBUTTONUP: self.track_mouse_pressed(event, False, log)
                case pygame.MOUSEWHEEL: self.handle_mousewheel_events(event, log)
                case _: self.log_unused_events(event, log)
            # Let UI subscribers handle the event
            # NOTE: kmod is stale. Call get_mods() when publishing.
            # self.publish(event, kmod)
            self.publish(event, self.kmod_simplify(pygame.key.get_mods()))

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

    def track_mouse_pressed(self,
                            event: pygame.event.Event,
                            is_pressed: bool,
                            log: logging.Logger
                            ) -> None:
        """Track mouse button state."""
        if is_pressed:
            event_str = "MOUSEBUTTONDOWN"
        else:
            event_str = "MOUSEBUTTONUP"
        log.debug(f"Event {event_str}, "
                  f"pos: {event.pos}, "
                  f"button: {event.button}")
        mouse_button = MouseButton.from_event(event)
        match mouse_button:
            case MouseButton.LEFT:
                self.mouse_pressed.left = is_pressed
            case MouseButton.MIDDLE:
                self.mouse_pressed.middle = is_pressed
            case MouseButton.RIGHT:
                self.mouse_pressed.right = is_pressed
            case _:
                log.debug(f"ERROR: Missing case for {mouse_button}")

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

    ##############
    # API FOR GAME
    ##############

    def kmod_simplify(self, kmod: int) -> int:
        """Filter out irrelevant keymods and combine left/right keymods.

        This reduces the many keymod left/right combinations to the following set:
            pygame.KMOD_NONE
            pygame.KMOD_SHIFT
            pygame.KMOD_CTRL
            pygame.KMOD_ALT
        """
        # Filter out irrelevant keymods
        kmod = kmod & (pygame.KMOD_ALT | pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
        # Turn LSHIFT and RSHIFT into just SHIFT
        if kmod & pygame.KMOD_SHIFT:
            kmod |= pygame.KMOD_SHIFT
        # Turn LCTRL and RCTRL into just CTRL
        if kmod & pygame.KMOD_CTRL:
            kmod |= pygame.KMOD_CTRL
        # Turn LALT and RALT into just ALT
        if kmod & pygame.KMOD_ALT:
            kmod |= pygame.KMOD_ALT
        return kmod
