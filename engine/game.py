"""Top-level game code."""
import sys                  # Exit with sys.exit()
import logging
import pygame
from .colors import Colors
from .geometry_types import Point2D, Vec2D
from .geometry_operators import CoordinateTransform
from .drawing_shapes import Line2D
from .timing import Timing
from .coord_sys import CoordinateSystem


class Game:
    """Game data is shared by all the code"""
    timing:                 Timing
    coord_sys:              CoordinateSystem
    window_surface:         pygame.Surface
    shapes:                 dict[str, list[Line2D]]
    mouse_button_1:         bool

    def __init__(self) -> None:
        self.setup()
        self.xfm = CoordinateTransform(self)

    def setup(self) -> None:
        """Create the game window."""
        pygame.init()
        pygame.font.init()
        self.coord_sys = CoordinateSystem(window_size=Vec2D(x=60*16, y=60*9))
        self.window_surface = pygame.display.set_mode(
                size=self.coord_sys.window_size.as_tuple(),
                flags=pygame.RESIZABLE
                )
        self.timing = Timing(clock=pygame.time.Clock())

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
        if self.mouse_button_1:
            # Update point where we have panned to
            mouse_pos = pygame.mouse.get_pos()
            self.coord_sys.pan_end = Point2D(x=mouse_pos[0], y=mouse_pos[1])
        self.draw_shapes()
        # Render
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        self.render_debug_hud()
        pygame.display.flip()
        # Delay to keep game at 60 FPS.
        self.timing.milliseconds_per_frame = self.timing.clock.tick(60)

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
        # mouse_p = Point2D(x=mouse_pos[0], y=mouse_pos[1])
        # mouse_g = self.xfm.pcs_to_gcs(mouse_p.as_vec())
        # origin_g = self.xfm.pcs_to_gcs(self.coord_sys.origin_p.as_vec())
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
                self.mouse_button_1 = True
                self.coord_sys.pan_start = Point2D(x=event.pos[0], y=event.pos[1])
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
                self.mouse_button_1 = False             # Finished panning
                self.coord_sys.origin_p = self.translation.as_point()  # Set the new origin
                self.coord_sys.pan_start = self.coord_sys.pan_end  # Zero-out the panning vector
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

    @property
    def panning(self) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=self.coord_sys.pan_start, end=self.coord_sys.pan_end)

    @property
    def translation(self) -> Vec2D:
        """Return the translation vector: adds mouse pan to origin offset."""
        return Vec2D(x=self.coord_sys.origin_p.x + self.panning.x,
                     y=self.coord_sys.origin_p.y + self.panning.y)

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
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
            return (f"origin: {self.coord_sys.origin_p}, "
                    f"translation: {self.translation}\n"
                    f"pan_start: {self.coord_sys.pan_start}, "
                    f"pan_end: {self.coord_sys.pan_end}\n"
                    )
        text += debug_pan()

        def debug_fps() -> str:
            # Display frame duration in milliseconds and rate in FPS
            # # TODO: update fps every N frames instead of every frame
            # fps = 1000 / self.timing.milliseconds_per_frame
            # # Use get_fps() for now -- it averages every 10 frames
            fps = self.timing.clock.get_fps()
            return f"frame: {self.timing.milliseconds_per_frame:d}ms ({fps:0.1f}FPS)"
        text += debug_fps()

        for i, line in enumerate(text.split('\n')):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
