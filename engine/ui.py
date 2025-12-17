"""User Interface."""
import sys                  # Exit with sys.exit()
import logging
from dataclasses import dataclass
import pygame
from .geometry_types import Vec2D, Point2D
from .panning import Panning


@dataclass
class UI:
    """Handle user interface events."""
    game:                   "Game"
    panning:                Panning = Panning()  # Track panning state
    mouse_button_1:         bool = False  # Track mouse button 1 down/up

    def handle_events(self, log: logging.Logger) -> None:
        """Handle events."""
        self.consume_event_queue(log)
        self.update_panning()

    def update_panning(self) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game view on the screen:
            renderer <-- xfm.gcs_to_pcs <-- coord_sys.translation <-- panning.vector

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.start
        """
        if self.panning.is_active:
            mouse_pos = pygame.mouse.get_pos()
            self.panning.end = Point2D.from_tuple(mouse_pos)

    def consume_event_queue(self, log: logging.Logger) -> None:
        """Consume all events on the event queue.

        All events are logged, including unused events.
        """
        game = self.game
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.KEYDOWN:
                    log.debug("Keydown")
                    sys.exit()
                case pygame.WINDOWSIZECHANGED:
                    # Update window size
                    game.coord_sys.window_size = Vec2D(x=event.x, y=event.y)
                    log.debug(f"Event WINDOWSIZECHANGED, new size: ({event.x}, {event.y})")
                case pygame.MOUSEBUTTONDOWN:
                    self.handle_mousebutton_down_events(event, log)
                case pygame.MOUSEBUTTONUP:
                    self.handle_mousebutton_up_events(event, log)
                case pygame.MOUSEWHEEL:
                    self.handle_mousewheel_events(event, log)
                case _:
                    self.log_unused_events(event, log)

    def zoom_out(self) -> None:
        """Zoom out.

        TODO: zoom about a point.
        Use mouse position to create an offset then add that to the origin. This is all in pixel
        coordinates.
        """
        game = self.game
        # mouse_pos = pygame.mouse.get_pos()
        # mouse_p = Point2D.from_tuple(mouse_pos)
        # mouse_g = self.xfm.pcs_to_gcs(mouse_p.as_vec())
        # origin_g = self.xfm.pcs_to_gcs(self.coord_sys.pcs_origin.as_vec())
        # translation = self.Vec2D.from_points(start=origin_g, end=mouse_g)
        game.coord_sys.gcs_width *= 1.1

    def zoom_in(self) -> None:
        """Zoom in.

        TODO: zoom about a point.
        """
        game = self.game
        game.coord_sys.gcs_width *= 0.9

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
                                       log: logging.Logger) -> None:
        """Handle event mouse button down."""
        log.debug("Event MOUSEBUTTONDOWN, "
                  f"pos: {event.pos}, "
                  f"button: {event.button}")
        match event.button:
            case 1:
                self.mouse_button_1 = True              # Left mouse button pressed
                self.panning.is_active = True           # Start panning
                self.panning.start = Point2D.from_tuple(event.pos)
            case _:
                pass

    def handle_mousebutton_up_events(self,
                                     event: pygame.event.Event,
                                     log: logging.Logger) -> None:
        """Handle event mouse button up."""
        game = self.game
        log.debug("Event MOUSEBUTTONUP, "
                  f"pos: {event.pos}, "
                  f"button: {event.button}")
        match event.button:
            case 1:
                self.mouse_button_1 = False             # Left mouse button released
                self.panning.is_active = False          # Stop panning
                game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
                self.panning.start = self.panning.end  # Zero-out the panning vector
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
