"""Top-level game code.

Abbreviations:
    GCS: Game Coordinate System
    PCS: Pixel Coordinate System
    xfm: transform
"""
import sys                  # Exit with sys.exit()
import logging
import pygame
from .colors import Colors
from .geometry_types import Point2D, Vec2D
from .geometry_operators import CoordinateTransform
from .drawing_shapes import Line2D
from .timing import Timing
from .coord_sys import CoordinateSystem
from .panning import Panning


class Game:
    """Game data is shared by all the code"""
    coord_sys:              CoordinateSystem
    window_surface:         pygame.Surface
    timing:                 Timing
    xfm:                    CoordinateTransform
    panning:                Panning
    shapes:                 dict[str, list[Line2D]]
    mouse_button_1:         bool

    def __init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        # Set up a clock to set frame rate and measure frame period
        self.timing = Timing()
        # Track panning state
        self.panning = Panning()
        # Set the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(panning=self.panning, window_size=Vec2D(x=60*16, y=60*9))
        # Get a window from the OS
        self.window_surface = pygame.display.set_mode(
                size=self.coord_sys.window_size.as_tuple(),
                flags=pygame.RESIZABLE
                )
        # Create 'xfm' for transforming between coordinate systems
        self.xfm = CoordinateTransform(coord_sys=self.coord_sys)

    def run(self, log: logging.Logger) -> None:
        """Run the game."""
        self.shapes = {}                                # Shape primitives
        self.mouse_button_1 = False                     # Track mouse button 1 down/up
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        self.handle_events(log)
        # Physics
        self.draw_shapes()
        # Render
        self.update_panning()
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        self.render_debug_hud()
        pygame.display.flip()
        # Delay to keep game at 60 FPS.
        self.timing.ms_per_frame = self.timing.clock.tick(60)

    def handle_events(self, log: logging.Logger) -> None:
        """Handle events."""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.KEYDOWN:
                    log.debug("Keydown")
                    sys.exit()
                case pygame.WINDOWSIZECHANGED:
                    # Update window size
                    self.coord_sys.window_size = Vec2D(x=event.x, y=event.y)
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
        # mouse_pos = pygame.mouse.get_pos()
        # mouse_p = Point2D.from_tuple(mouse_pos)
        # mouse_g = self.xfm.pcs_to_gcs(mouse_p.as_vec())
        # origin_g = self.xfm.pcs_to_gcs(self.coord_sys.pcs_origin.as_vec())
        # translation = self.Vec2D.from_points(start=origin_g, end=mouse_g)
        self.coord_sys.gcs_width *= 1.1

    def zoom_in(self) -> None:
        """Zoom in.

        TODO: zoom about a point.
        """
        self.coord_sys.gcs_width *= 0.9

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
        log.debug("Event MOUSEBUTTONUP, "
                  f"pos: {event.pos}, "
                  f"button: {event.button}")
        match event.button:
            case 1:
                self.mouse_button_1 = False             # Left mouse button released
                self.panning.is_active = False          # Stop panning
                self.coord_sys.pcs_origin = self.coord_sys.translation.as_point()  # Set new origin
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

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        # Convert all lines from GCS to PCS and draw lines to the screen.
        for line_g in self.shapes['lines']:
            # Convert GCS to PCS
            line_p = Line2D(start=self.xfm.gcs_to_pcs(line_g.start.as_vec()).as_point(),
                            end=self.xfm.gcs_to_pcs(line_g.end.as_vec()).as_point()
                            )
            # Render to screen
            pygame.draw.line(self.window_surface,
                             Colors.line,
                             line_p.start.as_tuple(),
                             line_p.end.as_tuple()
                             )

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        font = pygame.font.SysFont("RobotoMono", 15, bold=False)
        pos = (0, 0)
        text = ""

        def debug_window_size() -> str:
            # Display window size
            center = (self.coord_sys.window_size.x/2, self.coord_sys.window_size.y/2)
            return f"Window size: {self.coord_sys.window_size}, Center: {center} PCS\n"
        text += debug_window_size()

        def debug_mouse_position() -> str:
            """Return string with mouse position in game and pixel coordiantes."""
            # Get mouse position in pixel coordinates
            mouse_position_tuple = pygame.mouse.get_pos()
            mouse_position = Vec2D(x=mouse_position_tuple[0],
                                   y=mouse_position_tuple[1])
            # Get mouse position in game coordinates
            mouse_g = self.xfm.pcs_to_gcs(mouse_position)
            # Test transform by converting back to pixel coordinates
            mouse_p = self.xfm.gcs_to_pcs(mouse_g)
            return ("Mouse: "
                    f"({mouse_g.x:0.1f}, {mouse_g.y:0.1f}) GCS, "
                    f"({mouse_p.x:0.1f}, {mouse_p.y:0.1f}) PCS\n"
                    )
        text += debug_mouse_position()

        def debug_mouse_button() -> str:
            """Return string with mouse button state."""
            return ("Mouse buttons: "
                    f"1: {self.mouse_button_1}\n"
                    )
        text += debug_mouse_button()

        def debug_pan() -> str:
            """Return string with pan values."""
            return (f"origin: {self.coord_sys.pcs_origin}, "
                    f"translation: {self.coord_sys.translation}\n"
                    f"pan_start: {self.panning.start}, "
                    f"pan_end: {self.panning.end}\n"
                    )
        text += debug_pan()

        def debug_fps() -> str:
            # Display frame duration in milliseconds and rate in FPS
            # # TODO: update fps every N frames instead of every frame
            # fps = 1000 / self.timing.ms_per_frame
            # # Use get_fps() for now -- it averages every 10 frames
            fps = self.timing.clock.get_fps()
            return f"frame: {self.timing.ms_per_frame:d}ms ({fps:0.1f}FPS)"
        text += debug_fps()

        for i, line in enumerate(text.split('\n')):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
