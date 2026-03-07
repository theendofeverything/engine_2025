"""User interface events.

TODO: finish writing this docstring
Events:
    Window resized:
        See 'handle_windowsizechanged_events()'.
        Also see pygame documentation for 'pygame.event'.
    Key down/up:
        See 'subscriber_map_event_to_action()' in 'Game':
            'case pygame.KEYDOWN | pygame.KEYUP'
                'InputMapper.key_map'
                'Game.do_action_for_key_event()'
    Mouse button down/up:
        See 'subscriber_map_event_to_action()' in 'Game':
            'case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP'
                'InputMapper.mouse_map'
                'do_action_for_mouse_button_event()'

User actions:
    Panning:
        See 'Panning.start()'
        See 'Panning.stop()'
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
from typing import Callable
import pygame
from src.context import Context
from .geometry_types import Vec2D, Point2D
from .drawing_shapes import Line2D
from .colors import Colors

FILE = pathlib.Path(__file__).name
log = logging.getLogger(__name__)


class UI:
    """Handle user interface events.

    Some events, like pygame.QUIT, are handled by UI. But most events are published to whatever
    callbacks the Game registered with UI (via UI.subscribe()). "Publishing an event" just means the
    callback is called with two arguments: the event (pygame.event.Event) and the key modifiers (a
    bitfield of flags like pygame.KMOD_SHIFT).
    """
    subscribers:    list[Callable[[pygame.event.Event, int], None]] = []

    @classmethod
    def subscribe(cls, callback: Callable[[pygame.event.Event, int], None]) -> None:
        """Call UI.subscribe(callback) to register "callback" for receiving UI events."""
        cls.subscribers.append(callback)

    @classmethod
    def publish(cls, event: pygame.event.Event, kmod: int) -> None:
        """Publish the event to subscribers by calling all registered callbacks."""
        for subscriber in cls.subscribers:
            subscriber(event, kmod)

    @classmethod
    def consume_event_queue(cls) -> None:
        """Consume all events on the event queue.

        All events are logged, including unused events.
        """
        # kmod = pygame.key.get_mods()
        for event in pygame.event.get():
            # Handle event on the engine side
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.WINDOWSIZECHANGED: cls.handle_windowsizechanged_events(event)
                case pygame.MOUSEWHEEL: cls.handle_mousewheel_events(event)
                case _: cls.log_unused_events(event)
            # Let UI subscribers handle the event
            # NOTE: kmod is stale. Call get_mods() when publishing.
            # cls.publish(event, kmod)
            cls.publish(event, cls.kmod_simplify(pygame.key.get_mods()))

    @staticmethod
    def handle_windowsizechanged_events(event: pygame.event.Event) -> None:
        """User resized the window. Update origin and window size."""
        game = Context.game
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
        log.debug(f"... Context.renderer.window.size: {Context.renderer.window.size}")
        # NOTE: from pygame-ce docs:
        # Don't use window.get_surface() when using hardware rendering
        log.debug(f"... Context.renderer.window_surface.get_size(): "
                  f"{Context.renderer.window_surface.get_size()}")

    @classmethod
    def handle_mousewheel_events(cls, event: pygame.event.Event) -> None:
        """Handle mousewheel events."""
        match event.y:
            case -1:
                log.debug("ZOOM OUT")
                cls.zoom_out()
            case 1:
                log.debug("ZOOM IN")
                cls.zoom_in()
            case _:
                log.debug("Unexpected y-value")
        log.debug(f"Event MOUSEWHEEL, flipped: {event.flipped}, "
                  f"x:{event.x}, y:{event.y}, "
                  f"precise_x:{event.precise_x}, precise_y:{event.precise_y}")

    @staticmethod
    def log_unused_events(event: pygame.event.Event) -> None:
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

    @staticmethod
    def _zoom(scale: float) -> None:
        """Private zoom function used by zoom_in() and zoom_out().

        Zoom about a point: use mouse position to create an offset in GCS units before and after the
        zoom. Use the new zoom scale to convert the offset vector back to PCS units. Add the offset
        vector to the PCS origin. Be careful of the minus sign!
        """
        game = Context.game
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

    @classmethod
    def zoom_out(cls) -> None:
        """Zoom out."""
        cls._zoom(scale=1.1)

    @classmethod
    def zoom_in(cls) -> None:
        """Zoom in."""
        cls._zoom(scale=0.9)

    ##############
    # API FOR GAME
    ##############

    @staticmethod
    def kmod_simplify(kmod: int) -> int:
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
